import os
import re
import pickle
import argparse
import time
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

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
RRF_K = 60
CANDIDATE_TOP_K = 25
SIMILARITY_THRESHOLD = 0.0001
FALLBACK_RESPONSE = "I could not find the answer in the document."


# Global cache for sentence transformer model & BM25 index
_embedding_model = None
_bm25_index = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


def tokenize(text):
    return re.findall(r"\w+", text.lower())


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
        print("  [HF API] Status   : Connected [OK]")

    return _hf_client


# ============================================================
# LOAD FAISS & METADATA & BM25
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
    global _bm25_index
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

    if _bm25_index is None:
        corpus_tokens = [tokenize(c["text"]) for c in metadata["chunks"]]
        _bm25_index = BM25Okapi(corpus_tokens)
        print("  [BM25]      BM25 Index     : Initialized [OK]")

    return metadata


# ============================================================
# EMBEDDING VIA LOCAL SENTENCE TRANSFORMER
# ============================================================

def create_question_embedding(question, client=None):
    st_model = get_embedding_model()
    emb = st_model.encode([question], normalize_embeddings=True)[0]
    return np.array(emb, dtype=np.float32)


# ============================================================
# HYBRID RETRIEVAL (BM25 + RRF FUSION, k=60)
# ============================================================

def search_similar_chunks(question, index, metadata, k=K, client=None, rrf_k=RRF_K, candidate_k=CANDIDATE_TOP_K):
    chunks = metadata["chunks"]
    start_t = time.time()

    # 1. Dense Retrieval (Top 25)
    question_embedding = create_question_embedding(question, client)
    query_vector = np.array([question_embedding], dtype=np.float32)
    scores, indices = index.search(query_vector, min(candidate_k, index.ntotal))

    dense_ranks = {}
    dense_scores = {}
    for rank, idx in enumerate(indices[0]):
        if idx != -1:
            idx = int(idx)
            cid = chunks[idx].get("chunk_id", f"chunk_{idx}")
            dense_ranks[cid] = rank + 1
            dense_scores[cid] = float(scores[0][rank])

    # 2. BM25 Retrieval (Top 25)
    q_tokens = tokenize(question)
    bm25_scores = _bm25_index.get_scores(q_tokens)
    bm25_top_indices = np.argsort(bm25_scores)[::-1][:candidate_k]

    bm25_ranks = {}
    for rank, idx in enumerate(bm25_top_indices):
        idx = int(idx)
        cid = chunks[idx].get("chunk_id", f"chunk_{idx}")
        bm25_ranks[cid] = rank + 1

    # 3. Reciprocal Rank Fusion (RRF k=60)
    all_cids = set(dense_ranks.keys()).union(set(bm25_ranks.keys()))
    rrf_scores = {}
    for cid in all_cids:
        r_dense = dense_ranks.get(cid, None)
        r_bm25 = bm25_ranks.get(cid, None)

        score_dense = (1.0 / (rrf_k + r_dense)) if r_dense is not None else 0.0
        score_bm25 = (1.0 / (rrf_k + r_bm25)) if r_bm25 is not None else 0.0
        rrf_scores[cid] = score_dense + score_bm25

    # 4. Rank candidates by RRF score
    sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:k]
    elapsed = time.time() - start_t

    print()
    print(f"  [HYBRID]  BM25 + RRF Fusion Search (k_rrf={rrf_k})")
    print(f"  [HYBRID]  Candidates : Top-{candidate_k} Dense + Top-{candidate_k} BM25")
    print(f"  [HYBRID]  Search time: {elapsed*1000:.1f}ms  [OK]")

    chunk_map = {c.get("chunk_id", f"chunk_{i}"): (i, c) for i, c in enumerate(chunks)}

    results = []
    for rank, (cid, rrf_score) in enumerate(sorted_candidates, start=1):
        vec_idx, chunk = chunk_map[cid]
        doc_name = chunk.get("doc_name", "the_essential_south_indianCookbook.pdf")
        pages = chunk.get("pages", [chunk.get("estimated_page", 1)])
        primary_page = chunk.get("estimated_page", pages[0] if pages else 1)

        results.append({
            "rank": rank,
            "chunk_id": cid,
            "vector_index": vec_idx,
            "score": float(rrf_score),
            "dense_score": dense_scores.get(cid, 0.0),
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
    print("  [HF API]  Max new tokens : 180")
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
                max_tokens=180
            )

            elapsed = time.time() - start_t

            answer = response.choices[0].message.content.strip()

            print(
                f"  [HF API]  Response       : "
                f"{len(answer)} chars ({elapsed:.2f}s) [OK]"
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

def ask_question_rag(question, index_file=FAISS_INDEX_FILE, metadata_file=METADATA_FILE, k=K, similarity_threshold=SIMILARITY_THRESHOLD, hf_token=None):
    client = get_hf_client(hf_token)

    print()
    print("-" * 60)
    print(f"  Processing question: \"{question}\"")
    print("-" * 60)

    print()
    print("  STEP 1 : Loading vector store & BM25 index")
    index = load_faiss_index(index_file)
    metadata = load_metadata(metadata_file)

    print()
    print("  STEP 2 : Hybrid BM25 + RRF Search")
    results = search_similar_chunks(question, index, metadata, k=k, client=client)

    if not results:
        print()
        print("  [result]  No matching chunks found in index.")
        return {
            "answer": FALLBACK_RESPONSE,
            "sources": [],
            "max_score": 0.0,
            "results": []
        }

    max_score = max(r["score"] for r in results)

    print()
    print(f"  STEP 3 : Similarity threshold check")
    print(f"  [threshold]  Max RRF score        : {max_score:.6f}")
    print(f"  [threshold]  Threshold            : {similarity_threshold}")

    if max_score < similarity_threshold:
        print(f"  [threshold]  Result               : BELOW THRESHOLD -- Out of domain")
        print(f"  [threshold]  Action               : Returning fallback response")
        return {
            "answer": FALLBACK_RESPONSE,
            "sources": [],
            "max_score": max_score,
            "results": results,
            "threshold_triggered": True
        }

    print(f"  [threshold]  Result               : ABOVE THRESHOLD -- Proceeding [OK]")

    print()
    print("  STEP 4 : Generating answer via HF API")
    context = create_context(results)
    raw_answer = generate_answer(question, context, client)

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
        print(f"  [validate]  Answer validated with {len(sources)} source(s) [OK]")

    return {
        "answer": answer,
        "sources": sources,
        "max_score": max_score,
        "results": results,
        "threshold_triggered": False
    }


def print_ask_results(question, response):
    print()
    print("+" + "=" * 58 + "+")
    print(f"|  QUESTION: {question[:46]}")
    print("+" + "=" * 58 + "+")

    print()
    print("  RETRIEVED CHUNKS (Top-K):")
    print("  " + "-" * 56)
    for res in response["results"]:
        pages_str = ", ".join([f"Page {p}" for p in res["pages"]])
        print(f"  Rank {res['rank']}  |  RRF Score: {res['score']:.6f}  |  {res['doc_name']} ({pages_str})")
        snippet = res['text'][:120].replace('\n', ' ')
        print(f"           \"{snippet}...\"")
        print("  " + "-" * 56)

    print()
    print("  +--" + "-" * 54 + "--+")
    print("  |  FINAL ANSWER                                        |")
    print("  +--" + "-" * 54 + "--+")
    print()
    print(f"  {response['answer']}")

    print()
    print("  +--" + "-" * 54 + "--+")
    print("  |  SOURCE CITATIONS                                    |")
    print("  +--" + "-" * 54 + "--+")
    if response["sources"]:
        for src in response["sources"]:
            print(f"    -> {src}")
    else:
        print("    (No source citations -- Out of domain / Unanswered)")
    print()


# ============================================================
# CLI MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Ask questions to your documents using Hybrid RAG.")
    parser.add_argument("--question", type=str, help="Single question to answer")
    parser.add_argument("--index", type=str, default=FAISS_INDEX_FILE, help="FAISS index path")
    parser.add_argument("--metadata", type=str, default=METADATA_FILE, help="Metadata pkl path")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face API Token")
    args = parser.parse_args()

    print()
    print("+" + "=" * 58 + "+")
    print("|   ASK MY DOCUMENTS -- HYBRID RAG APPLICATION           |")
    print("|   Dense (all-MiniLM-L6-v2) + BM25 + RRF Fusion (k=60)  |")
    print("+" + "=" * 58 + "+")
    print()
    print(f"  Embedding model   : {EMBEDDING_MODEL}")
    print(f"  Generation model  : {GENERATION_MODEL}")
    print(f"  Top-K retrieval   : {K}")
    print(f"  FAISS index       : {args.index}")
    print(f"  Metadata          : {args.metadata}")

    if args.question:
        res = ask_question_rag(args.question, index_file=args.index, metadata_file=args.metadata, hf_token=args.token)
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
            res = ask_question_rag(question, index_file=args.index, metadata_file=args.metadata, hf_token=args.token)
            print_ask_results(question, res)
        except Exception as error:
            print(f"\n  ERROR: {error}")


if __name__ == "__main__":
    main()