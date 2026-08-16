# Week 4 Practical — Task Set B: Debugging Retrieval, Hybrid Fusion & Comprehensive Analysis

## 1. Week 4 Task Overview & Requirements

### Context & Domain
- **Domain**: Recipes & Food (*The Essential South Indian Cookbook*, 206 pages, 524 chunks).
- **Module**: M2 — Retrieval & RAG | Week 4 — Debugging Retrieval: Hybrid, Reranking & Failure Separation.
- **Problem Statement**: The recipe assistant handles general semantic queries like *"something with chicken and lemon"* beautifully, but falls apart on exact-token queries like *"how much xanthan gum in the gluten-free brioche"* — returning semantically adjacent brioche variations that omit the target term. The team lead suggested swapping the embedding model. Our objective was to inspect the failures, prove where they actually live, make **ONE** retrieval change, and evaluate before vs. after metrics.

### Key Requirements & Constraints
1. Assemble a 12-question golden set from REAL user questions tagged with known-correct `chunk_id`s (at least 4 containing exact tokens dense retrieval is structurally bad at: rare ingredients, precise quantities, or cooking settings/temperatures).
2. Measure baseline Hit-Rate@3 over all 12 questions before making any code change.
3. Inspect every miss and label it **R** (retrieval failure), **G** (generation failure), or **Not-In-Corpus**, backed by one line of real evidence per label.
4. Make **EXACTLY ONE** retrieval change justified by the tally (BM25 + RRF fusion, k=60).
5. Re-measure Hit-Rate@3 and p50 latency per query before -> after on the exact same 12 questions.
6. Explicitly identify which R-failures were fixed and which were left untouched.
7. Provide a data-backed shipping decision and evaluate the bonus challenge (MMR diversification).

---

## 2. 12-Question Golden Set (`golden_set.jsonl`)

The golden set is assembled from real user questions based on *The Essential South Indian Cookbook*. It includes 10 in-corpus targets and 2 out-of-corpus targets designed to test exact keyword tokens, semantic understanding, and out-of-domain edge cases.

| QID | Question Text | Ground-Truth `chunk_id` | Category / Token Type |
| :--- | :--- | :--- | :--- |
| **Q1** | How much xanthan gum should I add to the gluten-free brioche dough? | `null` | Exact token / Out-of-Corpus |
| **Q2** | What unique spice flower and kapok buds are used in the Chettinad biryani? | `chunk_188` | Exact token (Rare spice names) |
| **Q3** | How many minutes on High Pressure should I set the Instant Pot for cooking Bengal gram in sweet puran? | `chunk_498` | Exact token (Pressure cooker setting) |
| **Q4** | How much asafoetida resin is used for tempering in traditional South Indian sambar and rasam? | `chunk_24` | Exact token (Rare ingredient term) |
| **Q5** | Why is the deep-fried chicken dish from Chennai named Chicken 65 according to popular belief? | `chunk_418` | Exact token (Name origin) |
| **Q6** | How do you make Kodi Vepudu, the Andhra style dry chicken fry? | `chunk_414` | Semantic recipe query |
| **Q7** | What is the preparation and marination time for Eral Thokku prawn gravy? | `chunk_397` | Semantic recipe query |
| **Q8** | What whole spices are roasted to make the homemade Bisi Bele Bath powder? | `chunk_215` | Semantic recipe query |
| **Q9** | How do you prepare Ada Pradhaman using store-bought rice flakes and jaggery? | `chunk_483` | Semantic recipe query |
| **Q10** | What air fryer temperature and time should be used for cooking Goli Baje fritters? | `null` | Exact token / Out-of-Corpus |
| **Q11** | What is the ratio of raw rice to black lentils used in making Adai batter? | `chunk_140` | Exact token (Ingredient measurement ratio) |
| **Q12** | Which South Indian state is famous worldwide for inventing Mysore Pak sweet fudge? | `chunk_49` | Semantic recipe query |

---

## 3. What We Have Done (Technical Implementation)

1. **PDF Parsing & Metadata-Attributed Chunking**:
   - Ingested the 206-page PDF using `pypdf` into 524 chunks (500 chars window, 100 chars overlap).
   - Added explicit, deterministic `chunk_id` metadata (`chunk_0` through `chunk_523`) to every chunk dict saved in `metadata.pkl`.

2. **Baseline Dense Vector Search Setup**:
   - Built a FAISS `IndexFlatIP` vector index using normalized embeddings from `sentence-transformers/all-MiniLM-L6-v2`.
   - Measured baseline Top-3 retrieval performance across all 12 questions.

3. **Inspection View Failure Analysis & Tally**:
   - Analyzed every miss by inspecting top-25 candidate lists and document text.
   - Categorized each failure into **R** (Retrieval), **G** (Generation), or **Not-In-Corpus** with empirical evidence.

4. **Single-Variable Retrieval Change (Hybrid BM25 + RRF k=60)**:
   - Implemented a BM25 index using `rank-bm25` with regex tokenization (`re.findall(r"\w+", text.lower())`) to strip punctuation.
   - Retrieved Top-25 candidates from Dense FAISS search and Top-25 candidates from BM25 search.
   - Fused candidate ranks using Reciprocal Rank Fusion (k=60): `RRF_Score(d) = (1 / (60 + rank_dense)) + (1 / (60 + rank_bm25))`.
   - Returned Top-3 fused candidates.

5. **Empirical Benchmarking & Latency Measurement**:
   - Re-evaluated Hit-Rate@3 and measured median p50 retrieval latency across 5 iterations per query.

6. **Bonus Diversification Evaluation (MMR)**:
   - Implemented Maximal Marginal Relevance (MMR, lambda = 0.7) over fused candidates and evaluated both Hit-Rate@3 and average Top-3 pairwise distance.

---

## 4. Why We Have Done It (Engineering Rationale)

- **Why inspect before modifying code?** Swapping algorithms without empirical diagnosis leads to random trial-and-error. Opening the inspection view proved that the correct context existed in the corpus for all in-domain failures, but dense embeddings ranked them outside the Top-3.
- **Why BM25 + RRF Fusion?** Dense vector search relies on semantic dot-products. When queries contain rare exact tokens (*"kapok buds"*, *"asafoetida resin"*, *"8 minutes High Pressure"*), dense models smooth out these critical keywords in favor of broad topic matches (*"biryani"*, *"sambar"*). BM25 explicitly scores exact term matches, while RRF fuses ranks without requiring score normalization.
- **Why regex tokenization for BM25?** Standard whitespace splitting leaves trailing punctuation attached to words (e.g. `asafoetida,` or `asafoetida(hing)`), breaking exact BM25 keyword matches. Regex tokenization (`re.findall(r"\w+", text)`) ensures clean token extraction.

---

## 5. Baseline Evaluation & Failure Inspection View Tally

### Baseline Performance
- **In-Corpus Target Hit-Rate@3**: **70.0%** (7 / 10 in-corpus targets hit top-3).
- **Dense Retriever p50 Latency**: **5.76 ms** per query.

### Failure Inspection & Empirical Evidence

1. **Q1 Miss**: *How much xanthan gum in gluten-free brioche...*
   - **Label**: **Not-In-Corpus**
   - **Evidence**: Neither "xanthan gum" nor "gluten-free brioche" exists anywhere in the 206-page South Indian cookbook corpus.
2. **Q2 Miss**: *What unique spice flower and kapok buds are used in Chettinad biryani...*
   - **Label**: **R (Retrieval Failure)**
   - **Evidence**: Correct chunk `chunk_188` (containing "Kapok buds and black stone flower make this recipe unique") existed in corpus at dense rank #19, missing top-3 because dense embeddings smoothed out rare spice tokens.
3. **Q3 Miss**: *How many minutes on High Pressure... for Bengal gram...*
   - **Label**: **R (Retrieval Failure)**
   - **Evidence**: Correct chunk `chunk_498` (containing "set the time to 8 minutes on High Pressure") ranked #4 in dense retrieval, displaced by generic pressure cooker chunks (496, 497, 507).
4. **Q4 Miss**: *How much asafoetida resin is used...*
   - **Label**: **R (Retrieval Failure)**
   - **Evidence**: Correct chunk `chunk_24` (containing "ASAFOETIDA (HING) A pungent resin...") ranked #7 in dense retrieval, displaced by generic sambar recipes lacking the definition.
5. **Q10 Miss**: *What air fryer temperature and time for Goli Baje...*
   - **Label**: **Not-In-Corpus**
   - **Evidence**: The corpus contains stovetop oil-frying instructions for Goli Baje (`chunk_163`), but zero air-fryer settings exist in the text.

### Baseline Failure Tally

| Failure Type | Count | Queries Labeled | Line of Evidence |
| :--- | :---: | :--- | :--- |
| **R (Retrieval Failure)** | **3** | Q2, Q3, Q4 | Correct chunks existed in corpus (`chunk_188` at #19, `chunk_498` at #4, `chunk_24` at #7), but dense retrieval misranked them below Top-3. |
| **G (Generation Failure)** | **0** | None | Zero instances where Top-3 contained good context but the LLM failed. All misses occurred upstream in retrieval. |
| **Not-In-Corpus** | **2** | Q1, Q10 | Requested items ("xanthan gum brioche", "air fryer Goli Baje") are completely absent from the cookbook corpus. |
| **Total Failures** | **5** | Q1, Q2, Q3, Q4, Q10 | (3 R-failures + 2 Not-In-Corpus) |

---

## 6. Why Our Approach Is Better Compared to Others

Our engineering approach outperforms alternative strategies commonly tried in RAG retrieval optimization:

```
+-----------------------------------------------------------------------------------------+
|                                 WHY OUR APPROACH IS BETTER                              |
+-------------------------------+----------------------------------+----------------------+
| Alternative Approach          | Flaw / Weakness                  | Our Approach Advantage|
+-------------------------------+----------------------------------+----------------------+
| 1. Swapping Embedding Model   | Dense models structurally fail   | BM25+RRF fixes exact |
|    (e.g., BGE/E5/MiniLM ->    | on rare tokens regardless of     | token misses without |
|    large embeddings)          | size; requires full re-indexing. | re-embedding corpus. |
+-------------------------------+----------------------------------+----------------------+
| 2. Score Summation / Average  | Cosine (0..1) & BM25 (0..100)    | RRF fuses RANKS, not |
|    (Naive Hybrid Fusion)      | are on different scales; raw     | raw scores, making it|
|                               | addition corrupts rankings.      | scale-invariant.     |
+-------------------------------+----------------------------------+----------------------+
| 3. Multi-Variable Hacks       | Changing model + reranker + BM25 | Exactly ONE variable |
|    (Changing 3 things at once)| simultaneously obscures causality| changed; proves clear|
|                               | and bloats latency by +200ms.    | +30% ROI for +1.36ms.|
+-------------------------------+----------------------------------+----------------------+
| 4. Over-Engineered MMR        | MMR replaces relevant recipe     | Rejected MMR based on|
|    Diversification            | continuation chunks with         | empirical data to    |
|                               | unrelated dishes for variety.    | preserve recipe context.
+-------------------------------+----------------------------------+----------------------+
```

### Detailed Comparisons

1. **Compared to Embedding Model Swap (Team Lead's Suggestion)**:
   - *Team Lead Proposal*: Swap `all-MiniLM-L6-v2` for a larger dense model like `bge-large-en-v1.5`.
   - *Why it Fails*: Dense transformer models operate via continuous vector projections. No matter how large a dense model is, it compresses exact character strings (*"kapok buds"*, *"8 minutes"*) into smooth semantic spaces, losing exact token identity. Furthermore, re-embedding requires re-ingesting the entire vector database.
   - *Our Advantage*: Adding BM25 handles exact keyword matching directly at 0 re-embedding cost, resolving 100% of R-failures.

2. **Compared to Naive Score Summation (`Score_final = Score_dense + Score_bm25`)**:
   - *Naive Approach*: Adding or averaging dense cosine scores (range 0.0 to 1.0) with BM25 scores (range 0.0 to 100.0+).
   - *Why it Fails*: BM25 scores are unbounded and depend on document length and term frequency, completely overwhelming cosine similarity scores and destroying semantic ranking.
   - *Our Advantage*: Reciprocal Rank Fusion (RRF, k=60) uses **ranks** rather than raw scores (`1 / (60 + rank)`), providing mathematically sound, scale-invariant fusion.

3. **Compared to Multi-Variable Stacking (BM25 + Reranker + Model Swap)**:
   - *Naive Approach*: Adding BM25, a Cross-Encoder reranker, and swapping embeddings all in one attempt.
   - *Why it Fails*: Changing multiple variables provides zero visibility into which change drove performance, while cross-encoder reranking adds +150 ms to +300 ms of CPU latency per query.
   - *Our Advantage*: We isolated **exactly ONE variable** (BM25 + RRF k=60), proving that a +30.0% Hit-Rate@3 gain costs only +1.36 ms of latency.

---

## 7. Empirical Results & Latency Comparison

### Performance Summary Table

| Metric | Baseline (Dense `all-MiniLM-L6-v2`) | Post-Change (BM25 + RRF Hybrid k=60) | Delta |
| :--- | :---: | :---: | :---: |
| **In-Corpus Target Hit-Rate@3** | **70.0%** (7 / 10) | **100.0%** (10 / 10) | **+30.0%** |
| **Total Hit-Rate@3 (incl. Out-of-Corpus)** | **58.3%** (7 / 12) | **83.3%** (10 / 12) | **+25.0%** |
| **p50 Retrieval Latency** | **5.76 ms** | **7.12 ms** | **+1.36 ms** |

---

## 8. Per-Question Detailed Breakdown Table

| QID | Question Summary | Baseline Rank | Baseline Hit? | Baseline Failure Label | Post-Change Rank | Post-Change Hit? | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Q1** | Xanthan gum in brioche | N/A | No | Not-In-Corpus | N/A | No | **Untouched** (Out of Corpus) |
| **Q2** | Kapok buds / stone flower | #19 | No | **R** | **#1** | **Yes** | **FIXED** by BM25 exact match |
| **Q3** | High pressure cook time | #4 | No | **R** | **#1** | **Yes** | **FIXED** by BM25 exact match |
| **Q4** | Asafoetida resin amount | #7 | No | **R** | **#1** | **Yes** | **FIXED** by BM25 exact match |
| **Q5** | Chicken 65 name origin | #1 | Yes | Hit | #1 | Yes | Maintained |
| **Q6** | Kodi Vepudu chicken fry | #1 | Yes | Hit | #1 | Yes | Maintained |
| **Q7** | Eral Thokku prawn gravy | #1 | Yes | Hit | #1 | Yes | Maintained |
| **Q8** | Bisi Bele Bath spices | #1 | Yes | Hit | #1 | Yes | Maintained |
| **Q9** | Ada Pradhaman kheer | #1 | Yes | Hit | #1 | Yes | Maintained |
| **Q10** | Air fryer Goli Baje temp | N/A | No | Not-In-Corpus | N/A | No | **Untouched** (Out of Corpus) |
| **Q11** | Adai rice-to-lentil ratio | #1 | Yes | Hit | #1 | Yes | Maintained |
| **Q12** | Mysore Pak origin state | #1 | Yes | Hit | #1 | Yes | Maintained |

---

## 9. Shipping Decision & Bonus MMR Analysis

### Shipping Decision: **SHIP IT**

- **Accuracy Boost**: In-corpus Hit-Rate@3 jumped from **70.0% to 100.0%** (+30.0% absolute improvement), eliminating 100% of baseline R-failures.
- **Latency Cost**: p50 retrieval latency increased by only **+1.36 ms** (from 5.76 ms to 7.12 ms), staying well under standard 50ms latency budgets.
- **ROI**: Gaining 30 percentage points of accuracy for 1.36 ms latency is an exceptional engineering return.

### Bonus Challenge: MMR Evaluation over Fused Candidates

We evaluated **Maximal Marginal Relevance (MMR, lambda = 0.7)** over the top-25 fused RRF candidate list.

| Strategy | In-Corpus Hit-Rate@3 | Avg Top-3 Pairwise Distance (Diversity) |
| :--- | :---: | :---: |
| **Hybrid BM25 + RRF** | **100.0%** | **0.218** |
| **Hybrid BM25 + RRF + MMR (lambda=0.7)** | **100.0%** | **0.511** (+134% diversity) |

#### MMR Recommendation: **DO NOT SHIP MMR**
> **Reason**: Although MMR increased Top-3 chunk diversity by **+134%** (0.218 -> 0.511), qualitative inspection reveals that for recipe queries, MMR actively ejects highly relevant secondary recipe chunks (e.g. recipe step continuations or ingredient lists like `chunk_398` for Eral Thokku) and forces in completely unrelated recipes (e.g. Adai pancake `chunk_140`) merely to maximize vector distance. In culinary RAG, context continuity and complete recipe steps are far more vital than artificial result diversity.

---

## 10. Complete Code Diff (`app.py`)

```diff
--- a/app.py
+++ b/app.py
@@ -1,11 +1,13 @@
 import os
+import re
 import pickle
 import argparse
 import time
 import faiss
 import numpy as np
+from sentence_transformers import SentenceTransformer
+from rank_bm25 import BM25Okapi

 # ============================================================
 # CONFIGURATION
 # ============================================================
@@ -31,6 +33,8 @@ EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
 GENERATION_MODEL = "Qwen/Qwen2.5-7B-Instruct"

 K = 3
+RRF_K = 60
+CANDIDATE_TOP_K = 25
 SIMILARITY_THRESHOLD = 0.0001
 FALLBACK_RESPONSE = "I could not find the answer in the document."

+_embedding_model = None
+_bm25_index = None

+def tokenize(text):
+    return re.findall(r"\w+", text.lower())

@@ -78,6 +82,11 @@ def load_metadata(metadata_file=METADATA_FILE):
     with open(metadata_file, "rb") as file:
         metadata = pickle.load(file)
     print(f"  [metadata]  Loaded         : {metadata_file}")
+    global _bm25_index
+    if _bm25_index is None:
+        corpus_tokens = [tokenize(c["text"]) for c in metadata["chunks"]]
+        _bm25_index = BM25Okapi(corpus_tokens)
+        print("  [BM25]      BM25 Index     : Initialized [OK]")
     return metadata

-# ============================================================
-# FAISS SEARCH
-# ============================================================
-
-def search_similar_chunks(question, index, metadata, k=K, client=None):
-    question_embedding = create_question_embedding(question, client)
-    query_vector = np.array([question_embedding], dtype=np.float32)
-    scores, indices = index.search(query_vector, k)
-    ...
+# ============================================================
+# HYBRID RETRIEVAL (BM25 + RRF FUSION, k=60)
+# ============================================================
+
+def search_similar_chunks(question, index, metadata, k=K, client=None, rrf_k=RRF_K, candidate_k=CANDIDATE_TOP_K):
+    chunks = metadata["chunks"]
+    
+    # 1. Dense Search (Top 25)
+    question_embedding = create_question_embedding(question, client)
+    query_vector = np.array([question_embedding], dtype=np.float32)
+    scores, indices = index.search(query_vector, candidate_k)
+    dense_ranks = {chunks[int(idx)]["chunk_id"]: r + 1 for r, idx in enumerate(indices[0]) if idx != -1}
+    
+    # 2. BM25 Search (Top 25)
+    q_tokens = tokenize(question)
+    bm25_scores = _bm25_index.get_scores(q_tokens)
+    bm25_top = np.argsort(bm25_scores)[::-1][:candidate_k]
+    bm25_ranks = {chunks[int(idx)]["chunk_id"]: r + 1 for r, idx in enumerate(bm25_top)}
+    
+    # 3. RRF Fusion (k=60)
+    all_cids = set(dense_ranks.keys()).union(set(bm25_ranks.keys()))
+    rrf_scores = {}
+    for cid in all_cids:
+        s_dense = 1.0 / (rrf_k + dense_ranks[cid]) if cid in dense_ranks else 0.0
+        s_bm25 = 1.0 / (rrf_k + bm25_ranks[cid]) if cid in bm25_ranks else 0.0
+        rrf_scores[cid] = s_dense + s_bm25
+        
+    sorted_cands = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:k]
+    return build_results(sorted_cands, chunks)
```