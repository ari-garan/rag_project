import os
import pickle
import argparse
import time
import faiss
import numpy as np

from pypdf import PdfReader
from huggingface_hub import InferenceClient
from hf_config import ensure_hf_token, get_hf_token


# ============================================================
# CONFIGURATION & DEFAULTS
# ============================================================

PDF_FILE = "input/the_essential_south_indianCookbook.pdf"
VECTOR_STORE_DIR = "vector_store"

FAISS_INDEX_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "faiss_index.bin"
)

METADATA_FILE = os.path.join(
    VECTOR_STORE_DIR,
    "metadata.pkl"
)

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

BATCH_SIZE = 8


# ============================================================
# EXTRACT TEXT FROM PDF WITH EXACT PAGE MAPPING
# ============================================================

def extract_pdf_text(pdf_file):
    print()
    print("=" * 60)
    print("  STEP 1 : PDF TEXT EXTRACTION")
    print("=" * 60)
    print(f"  [pypdf]  Reading file    : {pdf_file}")

    if not os.path.exists(pdf_file):
        raise FileNotFoundError(
            f"\nPDF not found:\n{pdf_file}\n\n"
            "Please put your PDF inside the input folder "
            "or change PDF_FILE in pdf_to_vector.py."
        )

    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)

    print(f"  [pypdf]  Total pages     : {total_pages}")

    pages_data = []
    non_empty = 0
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text is None:
            text = ""
        text = text.strip()
        if text:
            non_empty += 1
        pages_data.append({
            "page_number": page_number,
            "text": text
        })

    print(f"  [pypdf]  Pages with text : {non_empty}/{total_pages}")
    print(f"  [pypdf]  Status          : Extraction complete ✓")

    return pages_data


def combine_pages_with_map(pages_data):
    complete_text = ""
    page_spans = []

    for page in pages_data:
        text = page["text"]
        if not text:
            continue

        start_pos = len(complete_text)
        complete_text += text + "\n\n"
        end_pos = len(complete_text)

        page_spans.append({
            "page_number": page["page_number"],
            "start": start_pos,
            "end": end_pos
        })

    return complete_text, page_spans


def get_pages_for_range(start_pos, end_pos, page_spans):
    matching_pages = []
    for span in page_spans:
        if max(span["start"], start_pos) < min(span["end"], end_pos):
            matching_pages.append(span["page_number"])
    if not matching_pages and page_spans:
        mid = (start_pos + end_pos) / 2.0
        closest = min(page_spans, key=lambda s: abs((s["start"] + s["end"]) / 2.0 - mid))
        matching_pages = [closest["page_number"]]
    return matching_pages if matching_pages else [1]


# ============================================================
# CREATE CHUNKS WITH PAGE ATTRIBUTION
# ============================================================

def create_chunks(text, page_spans, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP, doc_name="document"):
    if overlap >= chunk_size:
        raise ValueError("CHUNK_OVERLAP must be smaller than CHUNK_SIZE.")

    print()
    print("=" * 60)
    print("  STEP 2 : TEXT CHUNKING")
    print("=" * 60)
    print(f"  [chunker]  Document         : {doc_name}")
    print(f"  [chunker]  Total text chars  : {len(text):,}")
    print(f"  [chunker]  Chunk size        : {chunk_size} chars")
    print(f"  [chunker]  Chunk overlap     : {overlap} chars")
    print(f"  [chunker]  Step size         : {chunk_size - overlap} chars")

    chunks = []
    start = 0
    text_length = len(text)
    step = chunk_size - overlap

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk_text = text[start:end].strip()

        if chunk_text:
            pages = get_pages_for_range(start, end, page_spans)
            chunks.append({
                "text": chunk_text,
                "start": start,
                "end": end,
                "doc_name": doc_name,
                "pages": pages,
                "primary_page": pages[0] if pages else 1
            })

        start += step

    print(f"  [chunker]  Chunks created    : {len(chunks)}")
    print(f"  [chunker]  Page range        : Page 1 - Page {page_spans[-1]['page_number'] if page_spans else 1}")
    print(f"  [chunker]  Status            : Chunking complete ✓")

    return chunks


# ============================================================
# CREATE EMBEDDINGS VIA HUGGING FACE INFERENCE API
# ============================================================

def create_embeddings_api(chunks, token=None, model_name=EMBEDDING_MODEL):
    if not token:
        token = ensure_hf_token()

    client = InferenceClient(token=token)
    texts = [chunk["text"] for chunk in chunks]

    print()
    print("=" * 60)
    print("  STEP 3 : EMBEDDING VIA HUGGING FACE INFERENCE API")
    print("=" * 60)
    print(f"  [HF API]  Endpoint      : https://api-inference.huggingface.co")
    print(f"  [HF API]  Model         : {model_name}")
    print(f"  [HF API]  Pipeline      : feature_extraction")
    print(f"  [HF API]  Total chunks  : {len(texts)}")
    print(f"  [HF API]  Batch size    : {BATCH_SIZE}")
    print()

    embeddings = []
    total_batches = (len(texts) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        for attempt in range(5):
            try:
                start_t = time.time()
                res = client.feature_extraction(batch, model=model_name)
                elapsed = time.time() - start_t

                arr = np.array(res, dtype=np.float32)

                if arr.ndim == 3:
                    arr = np.mean(arr, axis=1)
                elif arr.ndim == 1:
                    arr = np.expand_dims(arr, axis=0)

                for vec in arr:
                    norm = np.linalg.norm(vec)
                    norm_vec = vec / max(norm, 1e-12)
                    embeddings.append(norm_vec)

                print(f"  [HF API]  feature_extraction  Batch {batch_num}/{total_batches}  "
                      f"({len(batch)} chunks)  {elapsed:.2f}s  ✓")
                break
            except Exception as err:
                print(f"  [HF API]  feature_extraction  Batch {batch_num}/{total_batches}  "
                      f"RETRY {attempt+1}/5  Error: {err}")
                time.sleep(3)

    embeddings = np.array(embeddings, dtype=np.float32)
    print()
    print(f"  [HF API]  Embedding shape    : {embeddings.shape}")
    print(f"  [HF API]  Embedding dim      : {embeddings.shape[1]}")
    print(f"  [HF API]  Total embedded     : {embeddings.shape[0]} chunks")
    print(f"  [HF API]  Status             : Embedding complete ✓")
    return embeddings


# ============================================================
# CREATE FAISS INDEX
# ============================================================

def create_faiss_index(embeddings):
    print()
    print("=" * 60)
    print("  STEP 4 : FAISS INDEX CREATION")
    print("=" * 60)

    dimension = embeddings.shape[1]
    print(f"  [FAISS]  Index type       : IndexFlatIP (Inner Product)")
    print(f"  [FAISS]  Vector dimension : {dimension}")

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(f"  [FAISS]  Vectors stored   : {index.ntotal}")
    print(f"  [FAISS]  Status           : Index created ✓")

    return index


# ============================================================
# SAVE FAISS INDEX
# ============================================================

def save_faiss_index(index, index_file=FAISS_INDEX_FILE):
    os.makedirs(os.path.dirname(index_file), exist_ok=True)
    faiss.write_index(index, index_file)

    size_kb = os.path.getsize(index_file) / 1024
    print()
    print(f"  [FAISS]  Index saved to  : {index_file}")
    print(f"  [FAISS]  File size       : {size_kb:.1f} KB")


# ============================================================
# SAVE METADATA
# ============================================================

def save_metadata(chunks, total_pages, total_text_length, metadata_file=METADATA_FILE, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, dimension=384):
    print()
    print("=" * 60)
    print("  STEP 5 : SAVING METADATA")
    print("=" * 60)

    metadata_chunks = []
    for chunk in chunks:
        metadata_chunks.append({
            "text": chunk["text"],
            "start_position": chunk["start"],
            "end_position": chunk["end"],
            "doc_name": chunk.get("doc_name", "document"),
            "pages": chunk.get("pages", [chunk.get("primary_page", 1)]),
            "estimated_page": chunk.get("primary_page", 1)
        })

    metadata = {
        "total_pages": total_pages,
        "total_text_length": total_text_length,
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "embedding_model": EMBEDDING_MODEL,
        "embedding_dimension": dimension,
        "chunks": metadata_chunks
    }

    os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
    with open(metadata_file, "wb") as file:
        pickle.dump(metadata, file)

    size_kb = os.path.getsize(metadata_file) / 1024
    print(f"  [metadata]  Saved to        : {metadata_file}")
    print(f"  [metadata]  File size       : {size_kb:.1f} KB")
    print(f"  [metadata]  Total chunks    : {len(metadata_chunks)}")
    print(f"  [metadata]  Chunk size      : {chunk_size}")
    print(f"  [metadata]  Chunk overlap   : {chunk_overlap}")
    print(f"  [metadata]  Embedding model : {EMBEDDING_MODEL}")
    print(f"  [metadata]  Embedding dim   : {dimension}")
    print(f"  [metadata]  Status          : Metadata saved ✓")


# ============================================================
# BUILD VECTOR STORE PIPELINE
# ============================================================

def build_vector_store(pdf_file=PDF_FILE, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, vector_store_dir=VECTOR_STORE_DIR, hf_token=None):
    if not hf_token:
        hf_token = ensure_hf_token()

    print()
    print("╔" + "=" * 58 + "╗")
    print("║   PDF TO VECTOR — RAG INGESTION PIPELINE                ║")
    print("║   Mode: Hugging Face Inference API (No local models)    ║")
    print("╚" + "=" * 58 + "╝")
    print()
    print(f"  Config:")
    print(f"    PDF file       : {pdf_file}")
    print(f"    Chunk size     : {chunk_size} chars")
    print(f"    Chunk overlap  : {chunk_overlap} chars")
    print(f"    Output dir     : {vector_store_dir}")
    print(f"    Embedding API  : {EMBEDDING_MODEL}")

    pipeline_start = time.time()

    pages_data = extract_pdf_text(pdf_file)
    total_pages = len(pages_data)

    complete_text, page_spans = combine_pages_with_map(pages_data)
    total_text_length = len(complete_text)

    doc_name = os.path.basename(pdf_file)
    chunks = create_chunks(complete_text, page_spans, chunk_size, chunk_overlap, doc_name=doc_name)

    embeddings = create_embeddings_api(chunks, token=hf_token)
    index = create_faiss_index(embeddings)

    index_path = os.path.join(vector_store_dir, "faiss_index.bin")
    metadata_path = os.path.join(vector_store_dir, "metadata.pkl")

    save_faiss_index(index, index_path)
    save_metadata(chunks, total_pages, total_text_length, metadata_path, chunk_size, chunk_overlap, dimension=embeddings.shape[1])

    pipeline_time = time.time() - pipeline_start

    print()
    print("╔" + "=" * 58 + "╗")
    print("║   PIPELINE COMPLETED SUCCESSFULLY ✓                    ║")
    print("╚" + "=" * 58 + "╝")
    print(f"  Total time       : {pipeline_time:.1f}s")
    print(f"  Chunks created   : {len(chunks)}")
    print(f"  Vectors stored   : {index.ntotal}")
    print(f"  Index file       : {index_path}")
    print(f"  Metadata file    : {metadata_path}")
    print()
    print(f"  Next step: python app.py")
    print()


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Ingest PDF and generate FAISS vector store via HF Inference API.")
    parser.add_argument("--pdf", type=str, default=PDF_FILE, help="Path to PDF file")
    parser.add_argument("--chunk-size", type=int, default=CHUNK_SIZE, help="Chunk size in characters")
    parser.add_argument("--chunk-overlap", type=int, default=CHUNK_OVERLAP, help="Chunk overlap in characters")
    parser.add_argument("--output-dir", type=str, default=VECTOR_STORE_DIR, help="Output vector store directory")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face API Token")
    args = parser.parse_args()

    build_vector_store(args.pdf, args.chunk_size, args.chunk_overlap, args.output_dir, hf_token=args.token)


if __name__ == "__main__":
    main()