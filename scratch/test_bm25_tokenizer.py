import os
import pickle
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vs_dir = os.path.join(base_dir, "vector_store")
faiss_file = os.path.join(vs_dir, "faiss_index.bin")
meta_file = os.path.join(vs_dir, "metadata.pkl")

index = faiss.read_index(faiss_file)
with open(meta_file, "rb") as f:
    metadata = pickle.load(f)

chunks = metadata["chunks"]
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def tokenize(text):
    return re.findall(r"\w+", text.lower())

corpus_tokens = [tokenize(c["text"]) for c in chunks]
bm25 = BM25Okapi(corpus_tokens)

golden_set = [
    {"id": "Q1", "question": "How much xanthan gum should I add to the gluten-free brioche dough?", "expected": None},
    {"id": "Q2", "question": "What unique spice flower and kapok buds are used in the Chettinad biryani?", "expected": "chunk_188"},
    {"id": "Q3", "question": "How many minutes on High Pressure should I set the Instant Pot for cooking Bengal gram in sweet puran?", "expected": "chunk_498"},
    {"id": "Q4", "question": "How much asafoetida resin is used for tempering in traditional South Indian sambar and rasam?", "expected": "chunk_24"},
    {"id": "Q5", "question": "Why is the deep-fried chicken dish from Chennai named Chicken 65 according to popular belief?", "expected": "chunk_418"},
    {"id": "Q6", "question": "How do you make Kodi Vepudu, the Andhra style dry chicken fry?", "expected": "chunk_414"},
    {"id": "Q7", "question": "What is the preparation and marination time for Eral Thokku prawn gravy?", "expected": "chunk_397"},
    {"id": "Q8", "question": "What whole spices are roasted to make the homemade Bisi Bele Bath powder?", "expected": "chunk_215"},
    {"id": "Q9", "question": "How do you prepare Ada Pradhaman using store-bought rice flakes and jaggery?", "expected": "chunk_483"},
    {"id": "Q10", "question": "What air fryer temperature and time should be used for cooking Goli Baje fritters?", "expected": None},
    {"id": "Q11", "question": "What is the ratio of raw rice to black lentils used in making Adai batter?", "expected": "chunk_140"},
    {"id": "Q12", "question": "Which South Indian state is famous worldwide for inventing Mysore Pak sweet fudge?", "expected": "chunk_49"}
]

print("=== BM25 ALONE WITH REGEX TOKENIZER ===")
for q in golden_set:
    exp = q["expected"]
    tokens = tokenize(q["question"])
    scores = bm25.get_scores(tokens)
    top_indices = np.argsort(scores)[::-1][:5]
    top_cids = [chunks[i]["chunk_id"] for i in top_indices]
    hit = exp in top_cids[:3] if exp else False
    print(f"[{q['id']}] Exp: {exp} | BM25 Top-3: {top_cids[:3]} | Hit? {hit}")

def hybrid_rrf(query, top_k_dense=25, top_k_bm25=25, k_rrf=60):
    q_emb = model.encode([query], normalize_embeddings=True)[0]
    scores, indices = index.search(np.array([q_emb], dtype=np.float32), top_k_dense)
    dense_res = {chunks[idx]["chunk_id"]: rank + 1 for rank, idx in enumerate(indices[0]) if idx != -1}
    
    tokens = tokenize(query)
    bm25_scores = bm25.get_scores(tokens)
    bm25_top = np.argsort(bm25_scores)[::-1][:top_k_bm25]
    bm25_res = {chunks[idx]["chunk_id"]: rank + 1 for rank, idx in enumerate(bm25_top)}
    
    all_cids = set(dense_res.keys()).union(set(bm25_res.keys()))
    rrf_scores = {}
    for cid in all_cids:
        r_dense = dense_res.get(cid, 999)
        r_bm25 = bm25_res.get(cid, 999)
        rrf_scores[cid] = (1.0 / (k_rrf + r_dense) if r_dense != 999 else 0.0) + (1.0 / (k_rrf + r_bm25) if r_bm25 != 999 else 0.0)
        
    sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    return [c[0] for c in sorted_candidates]

print("\n=== HYBRID RRF WITH REGEX TOKENIZER ===")
hits = 0
for q in golden_set:
    exp = q["expected"]
    top3 = hybrid_rrf(q["question"])
    hit = exp in top3 if exp else False
    if hit: hits += 1
    print(f"[{q['id']}] Exp: {exp} | Hybrid Top-3: {top3} | Hit? {hit}")

print(f"\nHybrid Hit-Rate@3: {hits}/10 ({hits/10*100:.1f}%)")
