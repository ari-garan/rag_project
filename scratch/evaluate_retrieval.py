import os
import pickle
import time
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# Load vector store and metadata
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vs_dir = os.path.join(base_dir, "vector_store")
faiss_file = os.path.join(vs_dir, "faiss_index.bin")
meta_file = os.path.join(vs_dir, "metadata.pkl")

index = faiss.read_index(faiss_file)
with open(meta_file, "rb") as f:
    metadata = pickle.load(f)

chunks = metadata["chunks"]
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Build BM25 index
corpus_tokens = [c["text"].lower().split() for c in chunks]
bm25 = BM25Okapi(corpus_tokens)

# Golden set definition
golden_set = [
    {
        "id": "Q1",
        "question": "How much xanthan gum should I add to the gluten-free brioche dough?",
        "expected_chunk_id": None,
        "type": "exact_token / out_of_corpus"
    },
    {
        "id": "Q2",
        "question": "What unique spice flower and kapok buds are used in the Chettinad biryani?",
        "expected_chunk_id": "chunk_188",
        "type": "exact_token"
    },
    {
        "id": "Q3",
        "question": "How many minutes on High Pressure should I set the Instant Pot for cooking Bengal gram in sweet puran?",
        "expected_chunk_id": "chunk_498",
        "type": "exact_token"
    },
    {
        "id": "Q4",
        "question": "How much asafoetida resin is used for tempering in traditional South Indian sambar and rasam?",
        "expected_chunk_id": "chunk_24",
        "type": "exact_token"
    },
    {
        "id": "Q5",
        "question": "Why is the deep-fried chicken dish from Chennai named Chicken 65 according to popular belief?",
        "expected_chunk_id": "chunk_418",
        "type": "exact_token"
    },
    {
        "id": "Q6",
        "question": "How do you make Kodi Vepudu, the Andhra style dry chicken fry?",
        "expected_chunk_id": "chunk_414",
        "type": "semantic"
    },
    {
        "id": "Q7",
        "question": "What is the preparation and marination time for Eral Thokku prawn gravy?",
        "expected_chunk_id": "chunk_397",
        "type": "semantic"
    },
    {
        "id": "Q8",
        "question": "What whole spices are roasted to make the homemade Bisi Bele Bath powder?",
        "expected_chunk_id": "chunk_215",
        "type": "semantic"
    },
    {
        "id": "Q9",
        "question": "How do you prepare Ada Pradhaman using store-bought rice flakes and jaggery?",
        "expected_chunk_id": "chunk_483",
        "type": "semantic"
    },
    {
        "id": "Q10",
        "question": "What air fryer temperature and time should be used for cooking Goli Baje fritters?",
        "expected_chunk_id": None,
        "type": "exact_token / out_of_corpus"
    },
    {
        "id": "Q11",
        "question": "What is the ratio of raw rice to black lentils used in making Adai batter?",
        "expected_chunk_id": "chunk_140",
        "type": "exact_token"
    },
    {
        "id": "Q12",
        "question": "Which South Indian state is famous worldwide for inventing Mysore Pak sweet fudge?",
        "expected_chunk_id": "chunk_49",
        "type": "semantic"
    }
]

# Dense Retrieval function (Baseline)
def retrieve_dense(query, top_k=25):
    q_emb = model.encode([query], normalize_embeddings=True)
    q_vec = np.array(q_emb, dtype=np.float32)
    scores, indices = index.search(q_vec, top_k)
    results = []
    for rank, idx in enumerate(indices[0]):
        if idx != -1:
            results.append({
                "chunk_id": chunks[idx]["chunk_id"],
                "score": float(scores[0][rank]),
                "rank": rank + 1,
                "text": chunks[idx]["text"]
            })
    return results

# BM25 Retrieval function
def retrieve_bm25(query, top_k=25):
    tokens = query.lower().split()
    scores = bm25.get_scores(tokens)
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for rank, idx in enumerate(top_indices):
        results.append({
            "chunk_id": chunks[idx]["chunk_id"],
            "score": float(scores[idx]),
            "rank": rank + 1,
            "text": chunks[idx]["text"]
        })
    return results

# RRF Fusion function (Single Change)
def retrieve_hybrid_rrf(query, top_k_dense=25, top_k_bm25=25, k_rrf=60, top_k_final=3):
    dense_res = retrieve_dense(query, top_k=top_k_dense)
    bm25_res = retrieve_bm25(query, top_k=top_k_bm25)
    
    rrf_scores = {}
    for r in dense_res:
        cid = r["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k_rrf + r["rank"]))
        
    for r in bm25_res:
        cid = r["chunk_id"]
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (k_rrf + r["rank"]))
        
    sorted_chunks = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:top_k_final]
    
    chunk_dict = {c["chunk_id"]: c for c in chunks}
    final_results = []
    for rank, (cid, score) in enumerate(sorted_chunks, start=1):
        final_results.append({
            "chunk_id": cid,
            "rrf_score": score,
            "rank": rank,
            "text": chunk_dict[cid]["text"]
        })
    return final_results

print("================================================================")
print("EVALUATING BASELINE (DENSE RETRIEVAL)")
print("================================================================")

baseline_hits = 0
baseline_eval = []
dense_latencies = []

for qitem in golden_set:
    q = qitem["question"]
    exp_cid = qitem["expected_chunk_id"]
    
    t0 = time.time()
    for _ in range(5):
        dense_top = retrieve_dense(q, top_k=25)
    t1 = time.time()
    dense_latencies.append((t1 - t0) / 5.0 * 1000)
    
    top3_cids = [r["chunk_id"] for r in dense_top[:3]]
    all_25_cids = [r["chunk_id"] for r in dense_top]
    
    is_hit = (exp_cid in top3_cids) if exp_cid is not None else False
    if is_hit:
        baseline_hits += 1
        rank = top3_cids.index(exp_cid) + 1
    else:
        rank = (all_25_cids.index(exp_cid) + 1) if (exp_cid is not None and exp_cid in all_25_cids) else None
        
    baseline_eval.append({
        "id": qitem["id"],
        "question": q,
        "expected": exp_cid,
        "top3": top3_cids,
        "is_hit": is_hit,
        "rank": rank
    })
    
    print(f"[{qitem['id']}] Question: {q[:50]}...")
    print(f"     Expected: {exp_cid} | Top-3 Retrieved: {top3_cids} | Hit? {is_hit} (Rank: {rank})")

valid_q_count = len([q for q in golden_set if q["expected_chunk_id"] is not None])
print(f"\nBaseline Hits (In-Corpus Target): {baseline_hits}/{valid_q_count} -> Hit-Rate@3: {baseline_hits/valid_q_count*100:.1f}%")
print(f"Dense p50 Latency: {np.median(dense_latencies):.2f} ms")

print("\n================================================================")
print("EVALUATING AFTER SINGLE CHANGE (BM25 + RRF FUSION, k=60)")
print("================================================================")

hybrid_hits = 0
hybrid_eval = []
hybrid_latencies = []

for qitem in golden_set:
    q = qitem["question"]
    exp_cid = qitem["expected_chunk_id"]
    
    t0 = time.time()
    for _ in range(5):
        hybrid_top = retrieve_hybrid_rrf(q, top_k_dense=25, top_k_bm25=25, k_rrf=60, top_k_final=3)
    t1 = time.time()
    hybrid_latencies.append((t1 - t0) / 5.0 * 1000)
    
    top3_cids = [r["chunk_id"] for r in hybrid_top]
    
    is_hit = (exp_cid in top3_cids) if exp_cid is not None else False
    if is_hit:
        hybrid_hits += 1
        rank = top3_cids.index(exp_cid) + 1
    else:
        rank = None
        
    hybrid_eval.append({
        "id": qitem["id"],
        "question": q,
        "expected": exp_cid,
        "top3": top3_cids,
        "is_hit": is_hit,
        "rank": rank
    })
    
    print(f"[{qitem['id']}] Question: {q[:50]}...")
    print(f"     Expected: {exp_cid} | Top-3 Retrieved: {top3_cids} | Hit? {is_hit} (Rank: {rank})")

print(f"\nHybrid Hits (In-Corpus Target): {hybrid_hits}/{valid_q_count} -> Hit-Rate@3: {hybrid_hits/valid_q_count*100:.1f}%")
print(f"Hybrid p50 Latency: {np.median(hybrid_latencies):.2f} ms")
