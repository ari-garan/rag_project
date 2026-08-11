# Hugging Face Inference API + FAISS RAG ("Ask My Documents")

## Topic B: Recipes & Food

A complete Retrieval-Augmented Generation system using the **Hugging Face Inference API** (no local model downloads).

### Tech Stack
- **PyPDF** — PDF text extraction
- **Hugging Face Inference API** — Embeddings (`all-MiniLM-L6-v2`) & Text Generation (`flan-t5-base`)
- **FAISS** — Vector similarity search
- **NumPy** — Array operations

### Key Feature: No local model downloads!
All model inference runs via **Hugging Face API calls** using your free HF_TOKEN.

---

## Project Structure

```text
rag_project/
├── input/
│   └── the_essential_south_indianCookbook.pdf
├── vector_store/
│   ├── faiss_index.bin
│   └── metadata.pkl
├── hf_config.py           # HF API Token management (.env or prompt)
├── pdf_to_vector.py       # PDF ingestion & embedding via HF API
├── app.py                 # RAG query app via HF API
├── evaluate_chunking.py   # Chunk size comparison tool
├── test_rag.py            # Automated end-to-end test suite
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 2. Get your free Hugging Face API Token

1. Go to https://huggingface.co/settings/tokens
2. Create a free token (read access is enough)
3. Either:
   - Create a `.env` file in the project root with: `HF_TOKEN=hf_your_token_here`
   - Or the app will prompt you to enter it on first run

### 3. Build the vector database

```powershell
python pdf_to_vector.py
```

### 4. Ask questions

```powershell
python app.py
```

### 5. Run chunk size comparison

```powershell
python evaluate_chunking.py
```

### 6. Run automated tests

```powershell
python test_rag.py
```

---

## Mentor Evaluation Checklist

| # | Criterion | How it's met |
|---|-----------|-------------|
| 1 | Can the app answer a question correctly? | Yes — retrieves top-3 chunks via FAISS, generates answer via FLAN-T5 API |
| 2 | Does every answer show the source document? | Yes — shows filename + exact page number |
| 3 | Does it admit it doesn't know for off-topic questions? | Yes — similarity threshold + prompt guard |
| 4 | Did they try more than one chunk size? | Yes — `evaluate_chunking.py` compares 250, 500, 1000 |