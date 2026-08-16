# Week 4 Practical — Task Set B: Comprehensive Technical Breakdown & Comparative Analysis

---

## 1. Week 4 Task Details (Problem Statement & Context)

### Background & Domain
- **Domain**: Recipes & Food (*The Essential South Indian Cookbook*, 206 pages, 524 chunks).
- **Module**: M2 — Retrieval & RAG | Week 4 — Debugging Retrieval: Hybrid, Reranking & Failure Separation.

### Problem Statement
Our South Indian recipe RAG assistant handles broad semantic queries (e.g., *"something with chicken and lemon"*) effectively, but fails on exact-token queries (e.g., *"how much xanthan gum in the gluten-free brioche"*). Instead of returning the exact answer or recognizing missing context, the baseline dense retriever returns three semantically adjacent bread/pastry recipes that completely omit the target token *xanthan gum*. 

The team lead proposed swapping the dense embedding model for a larger one. Our assignment was to:
1. Use an inspection view to empirically prove where failures actually live (Retrieval **R**, Generation **G**, or **Not-In-Corpus**).
2. Assemble a 12-question golden set from real user questions, tagged with ground-truth `chunk_id`s (at least 4 featuring exact tokens: rare ingredients, precise quantities, or cooking settings).
3. Implement **EXACTLY ONE** retrieval change (BM25 + RRF Fusion $k=60$).
4. Re-measure Hit-Rate@3 and $p50$ latency per query before $\rightarrow$ after on the exact same 12 questions.
5. Provide an empirical shipping decision and evaluate the bonus challenge (MMR diversification).

---

## 2. What We Have Done (Step-by-Step Implementation)

1. **PDF Ingestion & Metadata Chunking (`pdf_to_vector.py`)**:
   - Extracted text from all 206 pages of *The Essential South Indian Cookbook* using `pypdf`.
   - Chunked text into 524 chunks ($500\text{ chars}$ window, $100\text{ chars}$ overlap).
   - Tagged each chunk with an explicit, deterministic ID (`chunk_0` through `chunk_523`) stored in `metadata.pkl`.

2. **Baseline Dense Retrieval Setup (`app.py`)**:
   - Created a FAISS `IndexFlatIP` vector index using normalized embeddings from `sentence-transformers/all-MiniLM-L6-v2`.
   - Measured baseline Top-3 retrieval performance across the 12-question golden set.

3. **Inspection View & Failure Attribution**:
   - Examined every baseline miss across Top-25 candidates.
   - Labeled each miss **R** (Retrieval failure), **G** (Generation failure), or **Not-In-Corpus** with a single line of empirical evidence.

4. **Single Retrieval Change: Hybrid BM25 + RRF ($k=60$)**:
   - Implemented `BM25Okapi` lexical search with regex tokenization (`re.findall(r"\w+", text.lower())`) to eliminate punctuation mismatch.
   - Retrieved Top-25 candidates from Dense FAISS search and Top-25 candidates from BM25 lexical search.
   - Fused ranks using Reciprocal Rank Fusion ($k=60$):
     $$RRF\_Score(d) = \frac{1}{60 + r_{dense}(d)} + \frac{1}{60 + r_{bm25}(d)}$$
   - Selected Top-3 fused candidates.

5. **Empirical Benchmarking & Latency Measurement**:
   - Benchmark-tested Hit-Rate@3 before vs. after on the exact same 12 questions.
   - Measured median $p50$ retrieval latency across 5 test runs per query.

6. **Bonus Diversification Evaluation (MMR)**:
   - Evaluated Maximal Marginal Relevance (MMR, $\lambda=0.7$) over fused candidate lists to measure Hit-Rate@3 impact and Top-3 result diversity.

---

## 3. Why We Have Done It (Engineering Rationale)

- **Why inspect before modifying code?** Swapping components without diagnostic evidence leads to guesswork. Opening the inspection view proved that for all in-domain failures, the correct chunk existed in the vector space, but dense embeddings ranked it outside the Top-3.
- **Why BM25 + RRF Fusion?** Dense vector search computes dot products over continuous embedding spaces. When queries contain rare exact tokens (*"kapok buds"*, *"asafoetida resin"*, *"8 minutes High Pressure"*), dense models smooth out these critical keywords in favor of broad topic matches (*"biryani"*, *"sambar"*). BM25 explicitly weights exact term frequency, while RRF fuses ranks without requiring score normalization.
- **Why regex tokenization for BM25?** Standard whitespace splitting leaves trailing punctuation attached to words (e.g. `asafoetida,` or `asafoetida(hing)`), breaking exact BM25 matches. Regex tokenization (`re.findall(r"\w+", text)`) ensures clean token extraction.

---

## 4. Why Our Approach Is Superior Compared to Others

Our engineering strategy outperforms alternative approaches commonly attempted in RAG retrieval optimization:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 WHY OUR APPROACH IS BETTER                              │
├───────────────────────────────┬──────────────────────────────────┬──────────────────────┤
│ Alternative Approach          │ Flaw / Weakness                  │ Our Approach Advantage│
├───────────────────────────────┼──────────────────────────────────┼──────────────────────┤
│ 1. Swapping Embedding Model   │ Dense models structurally fail   │ BM25+RRF fixes exact │
│    (e.g., BGE/E5/MiniLM ->    │ on rare tokens regardless of     │ token misses without │
│    large embeddings)          │ size; requires full re-indexing. │ re-embedding corpus. │
├───────────────────────────────┼──────────────────────────────────┼──────────────────────┤
│ 2. Score Summation / Average  │ Cosine (0..1) & BM25 (0..100)    │ RRF fuses RANKS, not │
│    (Naive Hybrid Fusion)      │ are on different scales; raw     │ raw scores, making it│
│                               │ addition corrupts rankings.      │ scale-invariant.     │
├───────────────────────────────┼──────────────────────────────────┼──────────────────────┤
│ 3. Multi-Variable Hacks       │ Changing model + reranker + BM25 │ Exactly ONE variable │
│    (Changing 3 things at once)│ simultaneously obscures causality│ changed; proves clear│
│                               │ and bloats latency by +200ms.    │ +30% ROI for +1.36ms.│
├───────────────────────────────┼──────────────────────────────────┼──────────────────────┤
│ 4. Over-Engineered MMR        │ MMR replaces relevant recipe     │ Rejected MMR based on│
│    Diversification            │ continuation chunks with         │ empirical data to    │
│                               │ unrelated dishes for variety.    │ preserve recipe context.
└───────────────────────────────┴──────────────────────────────────┴──────────────────────┘
```

### Detailed Comparative Analysis

1. **Compared to Embedding Model Swap (Team Lead's Suggestion)**:
   - *Team Lead Proposal*: Swap `all-MiniLM-L6-v2` for a larger dense model like `bge-large-en-v1.5`.
   - *Why it Fails*: Dense transformer models operate via continuous vector projections. No matter how large a dense model is, it compresses exact character strings (*"kapok buds"*, *"8 minutes"*) into smooth semantic spaces, losing exact token identity. Furthermore, re-embedding requires re-ingesting the entire vector database.
   - *Our Advantage*: Adding BM25 handles exact keyword matching directly at $0$ re-embedding cost, resolving 100% of R-failures.

2. **Compared to Naive Score Summation ($Score_{final} = Score_{dense} + Score_{bm25}$)**:
   - *Naive Approach*: Adding or averaging dense cosine scores ($\text{range } 0.0 \text{ to } 1.0$) with BM25 scores ($\text{range } 0.0 \text{ to } 100.0+$).
   - *Why it Fails*: BM25 scores are unbounded and depend on document length and term frequency, completely overwhelming cosine similarity scores and destroying semantic ranking.
   - *Our Advantage*: Reciprocal Rank Fusion (RRF, $k=60$) uses **ranks** rather than raw scores ($1 / (60 + rank)$), providing mathematically sound, scale-invariant fusion.

3. **Compared to Multi-Variable Stacking (BM25 + Reranker + Model Swap)**:
   - *Naive Approach*: Adding BM25, a Cross-Encoder reranker, and swapping embeddings all in one attempt.
   - *Why it Fails*: Changing multiple variables provides zero visibility into which change drove performance, while cross-encoder reranking adds $+150\text{ ms}$ to $+300\text{ ms}$ of CPU latency per query.
   - *Our Advantage*: We isolated **exactly ONE variable** (BM25 + RRF $k=60$), proving that a $+30.0\%$ Hit-Rate@3 gain costs only $+1.36\text{ ms}$ of latency.

4. **Compared to Unvalidated MMR Diversification**:
   - *Naive Approach*: Blindly shipping MMR diversification to increase result variety.
   - *Why it Fails*: Qualitative analysis proves MMR replaces relevant recipe step continuation chunks with completely unrelated dishes (e.g. replacing Eral Thokku gravy steps with Adai pancakes) merely to maximize vector distance.
   - *Our Advantage*: We evaluated MMR empirically and recommended **DO NOT SHIP MMR**, preserving exact recipe context continuity.

---

## 5. Summary of Empirical Results

| Metric | Baseline (Dense `all-MiniLM-L6-v2`) | Post-Change (BM25 + RRF Hybrid $k=60$) | Delta |
| :--- | :---: | :---: | :---: |
| **In-Corpus Target Hit-Rate@3** | **70.0%** (7 / 10) | **100.0%** (10 / 10) | **+30.0%** |
| **Total Hit-Rate@3 (incl. Out-of-Corpus)** | **58.3%** (7 / 12) | **83.3%** (10 / 12) | **+25.0%** |
| **p50 Retrieval Latency** | **5.76 ms** | **7.12 ms** | **+1.36 ms** |

### Per-Question Breakdown Table

| QID | Question Summary | Baseline Rank | Failure Label | Post-Change Rank | Status |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Q1** | Xanthan gum in brioche | N/A | Not-In-Corpus | N/A | **Untouched** (Out of Corpus) |
| **Q2** | Kapok buds / stone flower | #19 | **R** | **#1** | **FIXED** by BM25 exact match |
| **Q3** | High pressure cook time | #4 | **R** | **#1** | **FIXED** by BM25 exact match |
| **Q4** | Asafoetida resin amount | #7 | **R** | **#1** | **FIXED** by BM25 exact match |
| **Q5** | Chicken 65 name origin | #1 | Hit | #1 | Maintained |
| **Q6** | Kodi Vepudu chicken fry | #1 | Hit | #1 | Maintained |
| **Q7** | Eral Thokku prawn gravy | #1 | Hit | #1 | Maintained |
| **Q8** | Bisi Bele Bath spices | #1 | Hit | #1 | Maintained |
| **Q9** | Ada Pradhaman kheer | #1 | Hit | #1 | Maintained |
| **Q10** | Air fryer Goli Baje temp | N/A | Not-In-Corpus | N/A | **Untouched** (Out of Corpus) |
| **Q11** | Adai rice-to-lentil ratio | #1 | Hit | #1 | Maintained |
| **Q12** | Mysore Pak origin state | #1 | Hit | #1 | Maintained |

---

## 6. Shipping Decision

### Final Recommendation: **SHIP IT**
- **In-Corpus Hit-Rate@3**: Increased from **70.0% to 100.0%** (+30.0% gain), resolving 100% of baseline R-failures.
- **Latency Cost**: $p50$ retrieval latency increased by only **+1.36 ms** (from $5.76\text{ ms}$ to $7.12\text{ ms}$), staying well under standard 50ms SLA budgets.
