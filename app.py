import os
import pickle
import argparse
import time
import json
import uuid
from datetime import datetime, timezone
import faiss
import numpy as np

from huggingface_hub import InferenceClient
from hf_config import ensure_hf_token


# ============================================================
# CONFIGURATION
# ============================================================

VECTOR_STORE_DIR = "vector_store"

FAISS_INDEX_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "faiss_index.bin"
)

METADATA_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "metadata.pkl"
)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GENERATION_MODEL = "Qwen/Qwen2.5-7B-Instruct"

K = 3
SIMILARITY_THRESHOLD = 0.30
FALLBACK_RESPONSE = "I could not find the answer in the document."
TRACE_SCHEMA_VERSION = "week5.trace.v1"
PROMPT_VERSION = "recipe-rag-v1"
GENERATION_PARAMS = {"max_tokens": 180, "temperature": 0.0}
DEFAULT_TRACE_FILE = os.path.join("traces", "requests.jsonl")


# ============================================================
# HUGGING FACE INFERENCE API CLIENT
# ============================================================

_hf_client = None


def get_hf_client(token=None):
    global _hf_client

    if _hf_client is None:
        if not token:
            token = ensure_hf_token()

        _hf_client = InferenceClient(
            token=token
        )

        print()
        print("  [HF API] InferenceClient initialized")
        print("  [HF API] Provider : Auto")
        print("  [HF API] Status   : Connected ✓")

    return _hf_client


# ============================================================
# LOAD FAISS & METADATA
# ============================================================

def load_faiss_index(index_file=FAISS_INDEX_FILE):
    if not os.path.exists(index_file):
        raise FileNotFoundError(
            f"\nFAISS index not found at {index_file}.\n"
            "Run 'python pdf_to_vector.py' first."
        )
    index = faiss.read_index(index_file)
    print(f"  [FAISS]  Index loaded     : {index_file}")
    print(f"  [FAISS]  Total vectors    : {index.ntotal}")
    return index


def load_metadata(metadata_file=METADATA_FILE):
    if not os.path.exists(metadata_file):
        raise FileNotFoundError(
            f"\nMetadata file not found at {metadata_file}.\n"
            "Run 'python pdf_to_vector.py' first."
        )
    with open(metadata_file, "rb") as file:
        metadata = pickle.load(file)
    print(f"  [metadata]  Loaded         : {metadata_file}")
    print(f"  [metadata]  Total chunks   : {len(metadata['chunks'])}")
    print(f"  [metadata]  Chunk size     : {metadata.get('chunk_size', 'N/A')}")
    print(f"  [metadata]  Embedding model: {metadata.get('embedding_model', 'N/A')}")
    return metadata


# ============================================================
# EMBEDDING VIA HF INFERENCE API
# ============================================================

def create_question_embedding(question, client=None):
    if client is None:
        client = get_hf_client()

    print()
    print(f"  [HF API]  feature_extraction")
    print(f"  [HF API]  Model    : {EMBEDDING_MODEL}")
    print(f"  [HF API]  Input    : \"{question[:80]}{'...' if len(question) > 80 else ''}\"")

    for attempt in range(5):
        try:
            start_t = time.time()
            res = client.feature_extraction(
                question,
                model=EMBEDDING_MODEL
            )
            elapsed = time.time() - start_t

            arr = np.array(res, dtype=np.float32)

            # Handle different response shapes
            if arr.ndim == 2:
                arr = np.mean(arr, axis=0)
            elif arr.ndim == 3:
                arr = np.mean(arr, axis=(0, 1))

            # Normalize
            norm = np.linalg.norm(arr)
            arr = arr / max(norm, 1e-12)

            print(f"  [HF API]  Response : {arr.shape[0]}-dim vector  ({elapsed:.2f}s)  ✓")
            return arr
        except Exception as err:
            print(f"  [HF API]  feature_extraction  RETRY {attempt+1}/5  Error: {err}")
            time.sleep(3)

    raise RuntimeError("Failed to get embedding from Hugging Face API after 5 retries.")


# ============================================================
# FAISS SEARCH
# ============================================================

def search_similar_chunks(question, index, metadata, k=K, client=None):
    question_embedding = create_question_embedding(question, client)
    query_vector = np.array([question_embedding], dtype=np.float32)

    actual_k = min(k, index.ntotal)

    print()
    print(f"  [FAISS]  Similarity search")
    print(f"  [FAISS]  Index type  : IndexFlatIP (Cosine Similarity)")
    print(f"  [FAISS]  Top-K       : {actual_k}")

    start_t = time.time()
    scores, indices = index.search(query_vector, actual_k)
    elapsed = time.time() - start_t

    print(f"  [FAISS]  Search time : {elapsed*1000:.1f}ms  ✓")

    chunks = metadata["chunks"]
    results = []

    for rank, vector_index in enumerate(indices[0]):
        if vector_index == -1:
            continue
        vector_index = int(vector_index)
        chunk = chunks[vector_index]

        doc_name = chunk.get("doc_name", "the_essential_south_indianCookbook.pdf")
        pages = chunk.get("pages", [chunk.get("estimated_page", 1)])
        primary_page = chunk.get("estimated_page", pages[0] if pages else 1)

        results.append({
            "rank": rank + 1,
            "vector_index": vector_index,
            "score": float(scores[0][rank]),
            "text": chunk["text"],
            "doc_name": doc_name,
            "pages": pages,
            "estimated_page": primary_page
        })

    return results


# ============================================================
# CONTEXT & PROMPT CREATION
# ============================================================

def create_context(results):
    context_parts = []
    for result in results:
        pages_str = ", ".join([f"Page {p}" for p in result["pages"]])
        context_parts.append(
            f"SOURCE: {result['doc_name']} ({pages_str})\n"
            f"{result['text']}"
        )
    return "\n\n".join(context_parts)


def create_prompt(question, context):
    return f"""Answer the question using ONLY the provided document context below.
If the answer cannot be found in the document context, answer exactly: {FALLBACK_RESPONSE}

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""


def make_trace_chunk(result):
    """Keep everything needed to inspect or reconstruct retrieved context."""
    return {
        "chunk_id": f"vector-{result['vector_index']}",
        "rank": result["rank"],
        "score": result["score"],
        "text": result["text"],
        "doc_name": result["doc_name"],
        "pages": result["pages"],
    }


def append_trace(trace, trace_file=DEFAULT_TRACE_FILE):
    """Append one complete, JSONL trace without logging secrets."""
    trace_dir = os.path.dirname(trace_file)
    if trace_dir:
        os.makedirs(trace_dir, exist_ok=True)
    with open(trace_file, "a", encoding="utf-8") as file:
        file.write(json.dumps(trace, ensure_ascii=False) + "\n")
    print(f"  [trace]   Saved trace      : {trace['trace_id']} -> {trace_file}")


# ============================================================
# GENERATE ANSWER VIA HF INFERENCE API
# ============================================================

def generate_answer(question, context, client=None):
    if client is None:
        client = get_hf_client()

    prompt = create_prompt(question, context)

    print()
    print("  [HF API]  chat_completion")
    print(f"  [HF API]  Model          : {GENERATION_MODEL}")
    print(f"  [HF API]  Max new tokens : {GENERATION_PARAMS['max_tokens']}")
    print(f"  [HF API]  Temperature    : {GENERATION_PARAMS['temperature']}")
    print(f"  [HF API]  Prompt length  : {len(prompt)} chars")

    for attempt in range(5):
        try:
            start_t = time.time()

            response = client.chat.completions.create(
                model=GENERATION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                **GENERATION_PARAMS
            )

            elapsed = time.time() - start_t

            answer = response.choices[0].message.content.strip()

            print(
                f"  [HF API]  Response       : "
                f"{len(answer)} chars ({elapsed:.2f}s) ✓"
            )

            return answer

        except Exception as err:
            print(
                f"  [HF API]  chat_completion "
                f"RETRY {attempt + 1}/5"
            )
            print(f"  Error type : {type(err).__name__}")
            print(f"  Error      : {repr(err)}")

            time.sleep(3)

    raise RuntimeError(
        "Failed to generate answer from Hugging Face API after 5 retries."
    )


# ============================================================
# MAIN RAG ANSWER LOGIC
# ============================================================

def ask_question_rag(question, index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE,
                     k=K, similarity_threshold=SIMILARITY_THRESHOLD, hf_token=None,
                     trace_file=DEFAULT_TRACE_FILE):
    client = get_hf_client(hf_token)

    print()
    print("-" * 60)
    print(f"  Processing question: \"{question}\"")
    print("-" * 60)

    print()
    print("  STEP 1 : Loading vector store")
    index = load_faiss_index(index_file)
    metadata = load_metadata(metadata_file)

    print()
    print("  STEP 2 : Embedding question via HF API")
    results = search_similar_chunks(question, index, metadata, k=k, client=client)

    if not results:
        print()
        print("  [result]  No matching chunks found in FAISS index.")
        response = {
            "answer": FALLBACK_RESPONSE,
            "sources": [],
            "max_score": 0.0,
            "results": []
        }
        if trace_file:
            append_trace({
                "schema_version": TRACE_SCHEMA_VERSION,
                "trace_id": str(uuid.uuid4()),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "question": question,
                "prompt_version": PROMPT_VERSION,
                "prompt": None,
                "retrieved_chunks": [],
                "generation": {"model": GENERATION_MODEL, "params": GENERATION_PARAMS},
                "raw_output": None,
                "final_output": response["answer"],
                "threshold": {"value": similarity_threshold, "max_score": 0.0, "triggered": False},
            }, trace_file)
        return response

    max_score = max(r["score"] for r in results)

    print()
    print(f"  STEP 3 : Similarity threshold check")
    print(f"  [threshold]  Max similarity score : {max_score:.4f}")
    print(f"  [threshold]  Threshold            : {similarity_threshold}")

    # Similarity Threshold Guard
    if max_score < similarity_threshold:
        print(f"  [threshold]  Result               : BELOW THRESHOLD — Out of domain")
        print(f"  [threshold]  Action               : Returning fallback response")
        response = {
            "answer": FALLBACK_RESPONSE,
            "sources": [],
            "max_score": max_score,
            "results": results,
            "threshold_triggered": True
        }
        if trace_file:
            append_trace({
                "schema_version": TRACE_SCHEMA_VERSION,
                "trace_id": str(uuid.uuid4()),
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "question": question,
                "prompt_version": PROMPT_VERSION,
                "prompt": None,
                "retrieved_chunks": [make_trace_chunk(r) for r in results],
                "generation": {"model": GENERATION_MODEL, "params": GENERATION_PARAMS},
                "raw_output": None,
                "final_output": response["answer"],
                "threshold": {"value": similarity_threshold, "max_score": max_score, "triggered": True},
            }, trace_file)
        return response

    print(f"  [threshold]  Result               : ABOVE THRESHOLD — Proceeding ✓")

    print()
    print("  STEP 4 : Generating answer via HF API")
    context = create_context(results)
    prompt = create_prompt(question, context)
    raw_answer = generate_answer(question, context, client)

    # Check if model output indicates missing info
    print()
    print("  STEP 5 : Validating answer")
    lower_ans = raw_answer.lower()
    if "could not find" in lower_ans or "not mentioned" in lower_ans or "cannot be found" in lower_ans or "not in the document" in lower_ans:
        answer = FALLBACK_RESPONSE
        sources = []
        print(f"  [validate]  Model indicated no answer found in context")
    else:
        answer = raw_answer
        sources = []
        for r in results:
            for p in r["pages"]:
                src_str = f"{r['doc_name']} (Page {p})"
                if src_str not in sources:
                    sources.append(src_str)
        print(f"  [validate]  Answer validated with {len(sources)} source(s) ✓")

    response = {
        "answer": answer,
        "sources": sources,
        "max_score": max_score,
        "results": results,
        "threshold_triggered": False
    }
    if trace_file:
        append_trace({
            "schema_version": TRACE_SCHEMA_VERSION,
            "trace_id": str(uuid.uuid4()),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "question": question,
            "prompt_version": PROMPT_VERSION,
            "prompt": prompt,
            "retrieved_chunks": [make_trace_chunk(r) for r in results],
            "generation": {"model": GENERATION_MODEL, "params": GENERATION_PARAMS},
            "raw_output": raw_answer,
            "final_output": response["answer"],
            "threshold": {"value": similarity_threshold, "max_score": max_score, "triggered": False},
        }, trace_file)
    return response


def print_ask_results(question, response):
    print()
    print("╔" + "=" * 58 + "╗")
    print(f"║  QUESTION: {question[:46]}")
    print("╚" + "=" * 58 + "╝")

    print()
    print("  RETRIEVED CHUNKS (Top-K):")
    print("  " + "-" * 56)
    for res in response["results"]:
        pages_str = ", ".join([f"Page {p}" for p in res["pages"]])
        print(f"  Rank {res['rank']}  |  Score: {res['score']:.4f}  |  {res['doc_name']} ({pages_str})")
        snippet = res['text'][:120].replace('\n', ' ')
        print(f"           \"{snippet}...\"")
        print("  " + "-" * 56)

    print()
    print("  ┌" + "─" * 56 + "┐")
    print("  │  FINAL ANSWER                                        │")
    print("  └" + "─" * 56 + "┘")
    print()
    print(f"  {response['answer']}")

    print()
    print("  ┌" + "─" * 56 + "┐")
    print("  │  SOURCE CITATIONS                                    │")
    print("  └" + "─" * 56 + "┘")
    if response["sources"]:
        for src in response["sources"]:
            print(f"    → {src}")
    else:
        print("    (No source citations — Out of domain / Unanswered)")
    print()


# ============================================================
# CLI MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Ask questions to your documents using RAG (HF Inference API).")
    parser.add_argument("--question", type=str, help="Single question to answer")
    parser.add_argument("--index", type=str, default=FAISS_INDEX_FILE, help="FAISS index path")
    parser.add_argument("--metadata", type=str, default=METADATA_FILE, help="Metadata pkl path")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face API Token")
    parser.add_argument("--trace-file", type=str, default=DEFAULT_TRACE_FILE,
                        help="JSONL trace destination (use --no-trace to disable)")
    parser.add_argument("--no-trace", action="store_true", help="Do not persist request traces")
    args = parser.parse_args()

    print()
    print("╔" + "=" * 58 + "╗")
    print("║   ASK MY DOCUMENTS — RAG Application                   ║")
    print("║   Powered by Hugging Face Inference API                 ║")
    print("╚" + "=" * 58 + "╝")
    print()
    print(f"  Embedding model   : {EMBEDDING_MODEL}")
    print(f"  Generation model  : {GENERATION_MODEL}")
    print(f"  Top-K retrieval   : {K}")
    print(f"  Similarity cutoff : {SIMILARITY_THRESHOLD}")
    print(f"  FAISS index       : {args.index}")
    print(f"  Metadata          : {args.metadata}")

    if args.question:
        res = ask_question_rag(args.question, index_file=args.index, metadata_file=args.metadata,
                               hf_token=args.token,
                               trace_file=None if args.no_trace else args.trace_file)
        print_ask_results(args.question, res)
        return

    print()
    print("  Type your question below. Type 'exit' to stop.")
    print()

    while True:
        try:
            question = input("  Ask a question: ").strip()
        except KeyboardInterrupt:
            print("\n\n  Exiting...")
            break

        if not question:
            continue

        if question.lower() in ["exit", "quit", "bye"]:
            print("\n  Goodbye!")
            break

        try:
            res = ask_question_rag(question, index_file=args.index, metadata_file=args.metadata,
                                   hf_token=args.token,
                                   trace_file=None if args.no_trace else args.trace_file)
            print_ask_results(question, res)
        except Exception as error:
            print(f"\n  ERROR: {error}")


if __name__ == "__main__":
    main()
