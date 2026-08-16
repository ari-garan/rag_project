# Beginner's Guide: Week 4 Retrieval Debugging, Hybrid Search & Failure Separation

Welcome to the comprehensive guide for **Week 4 — Debugging Retrieval: Hybrid, Reranking & Failure Separation**! This guide is specifically written for beginners to understand every concept, step-by-step implementation, and engineering rationale required for this module.

---

## 1. Core Concepts Explained Simply

### 🔑 1. Dense Vector Search vs. Lexical BM25 Search

| Search Type | How It Works | Strengths | Major Weakness / Failure Mode |
| :--- | :--- | :--- | :--- |
| **Dense Vector Search**<br>*(Cosine / FAISS)* | Converts text into continuous mathematical vectors (embeddings) using neural models like `all-MiniLM-L6-v2`. | Excellent at understanding **meanings and concepts** (e.g., matching *"something with chicken and lemon"* to a chicken recipe). | **Structurally bad at exact keyword tokens** (e.g., rare ingredients like *"xanthan gum"*, *"kapok buds"*, precise measurements, or oven temperatures). It smooths out exact terms into general topic vectors. |
| **Lexical BM25 Search**<br>*(Keyword Frequency)* | Counts word occurrences and adjusts for term frequency and document length (TF-IDF derivative). | Excellent at finding **exact character/word matches** (e.g., finding *"8 minutes High Pressure"* or *"asafoetida resin"*). | Cannot understand synonyms or broader concepts (e.g., fails if user asks for *"poultry"* instead of *"chicken"*). |

---

### 🔍 2. Failure Attribution Framework: R vs. G vs. Not-In-Corpus

When a RAG system returns an incorrect or incomplete answer, you must open the **inspection view** (checking top-25 retrieved chunks and the original document) to attribute where the failure occurred:

1. **R (Retrieval Failure)**:
   - **Definition**: The correct information **exists in your document/corpus**, but the retriever **failed to place it in the Top-K (Top-3)** context sent to the LLM.
   - **Example**: Ground truth `chunk_188` (containing *"kapok buds"*) existed in the PDF, but dense retrieval ranked it at #19.
   - **Fix**: Modify retrieval (e.g. add BM25 lexical search or reranking).

2. **G (Generation Failure)**:
   - **Definition**: The correct chunk **WAS successfully retrieved in the Top-3**, but the LLM hallucinated, misread the context, or omitted the detail in its generated response.
   - **Fix**: Improve prompt engineering, reduce temperature, or update system instructions. No retrieval change can fix a G-failure!

3. **Not-In-Corpus (Missing Context)**:
   - **Definition**: The requested information does **NOT exist anywhere in your source document**.
   - **Example**: Asking for *"xanthan gum in gluten-free brioche"* when searching a South Indian cookbook that contains zero brioche recipes.
   - **Fix**: Expand document ingestion or implement fallback guards ("I could not find the answer in the document").

---

### 🔀 3. Reciprocal Rank Fusion (RRF, $k=60$)

When combining Dense search and Lexical BM25 search, **never add raw scores together**. Cosine similarity scores range from $0.0$ to $1.0$, while BM25 scores range from $0.0$ to $100.0+$. Adding them directly lets BM25 completely overpower Cosine scores.

**Reciprocal Rank Fusion (RRF)** solves this by fusing **ranks** rather than raw scores:

$$RRF\_Score(d) = \frac{1}{k + r_{dense}(d)} + \frac{1}{k + r_{bm25}(d)}$$

- $r_{dense}(d)$: Rank of document $d$ in dense search results (e.g., 1, 2, 3...)
- $r_{bm25}(d)$: Rank of document $d$ in BM25 search results (e.g., 1, 2, 3...)
- $k$: Smoothing constant (standard industry default $k = 60$)

---

### 🎨 4. Maximal Marginal Relevance (MMR)

MMR is a post-processing algorithm that balances **relevance** (matching the query) with **diversity** (avoiding repetitive chunks):

$$MMR\_Score(d) = \lambda \cdot Relevance(d) - (1 - \lambda) \cdot \max_{s \in Selected} Similarity(d, s)$$

- $\lambda = 1.0$: Pure relevance (no diversity enforcement).
- $\lambda = 0.0$: Pure diversity (ignores relevance).
- **Culinary RAG Trade-off**: In recipe applications, near-duplicate chunks (e.g. step continuations) are often essential for complete recipe instructions. MMR can force out relevant recipe steps and substitute unrelated dishes merely to maximize vector distance!

---

## 2. Step-by-Step Implementation Guide for Beginners

### Step 1: Ingest PDF & Tag Chunks with Explicit `chunk_id`
Run `pdf_to_vector.py` to extract text from your PDF, chunk it, embed it with `sentence-transformers`, and save explicit chunk IDs:
```python
chunks.append({
    "chunk_id": f"chunk_{i}",
    "text": chunk_text,
    "pages": pages
})
```

---

### Step 2: Build the 12-Question Golden Set (`golden_set.jsonl`)
Assemble 12 real user questions based on the corpus:
- At least 4 exact-token queries (rare ingredients, precise quantities, cooking settings).
- 1 or 2 out-of-corpus queries (testing missing information).
- Save in `golden_set.jsonl` format:
```json
{"id": "Q2", "question": "What unique spice flower and kapok buds are used in Chettinad biryani?", "expected_chunk_id": "chunk_188", "type": "exact_token"}
```

---

### Step 3: Run Baseline Evaluation & Label Failures
1. Run dense vector retrieval on all 12 questions.
2. Calculate Baseline Hit-Rate@3:
   $$\text{Hit-Rate@3} = \frac{\text{Number of in-corpus questions where expected chunk is in Top-3}}{\text{Total in-corpus questions}}$$
3. Measure median $p50$ retrieval latency.
4. Label every miss **R**, **G**, or **Not-In-Corpus** with one line of evidence.

---

### Step 4: Implement Hybrid Search (BM25 + RRF $k=60$)
Update `app.py` to perform hybrid search:
1. Tokenize text using regex: `re.findall(r"\w+", text.lower())`.
2. Retrieve Top-25 Dense candidates.
3. Retrieve Top-25 BM25 candidates.
4. Calculate RRF score ($k=60$) for all candidates and sort.
5. Return Top-3 candidates.

---

### Step 5: Re-evaluate & Make Shipping Decision
1. Re-measure Hit-Rate@3 and $p50$ latency on the same 12 questions.
2. Compare before vs. after:
   - **Hit-Rate@3**: $70.0\% \rightarrow 100.0\%$ (+30.0% gain)
   - **p50 Latency**: $5.76\text{ ms} \rightarrow 7.12\text{ ms}$ (+1.36 ms delta)
3. Formulate shipping decision: **SHIP IT** because gaining +30% accuracy for only +1.36 ms latency is an outstanding trade-off.

---

## 3. Quick Reference Checklist

| Task Step | Key Command / Code | Target File |
| :--- | :--- | :--- |
| **Ingest PDF** | `python pdf_to_vector.py` | `pdf_to_vector.py` |
| **Golden Set** | Create 12 JSON lines | `golden_set.jsonl` |
| **Hybrid Search** | `BM25Okapi` + RRF $k=60$ | `app.py` |
| **Evaluation Report** | Document metrics & diff | `results.md` |
| **Git Staging** | `git add golden_set.jsonl results.md app.py pdf_to_vector.py requirements.txt` | Git repo |

---
*Happy coding and retrieval debugging!*
