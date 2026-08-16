import os
import pickle
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

# Embed all chunks for MMR diversity computation
chunk_texts = [c["text"] for c in chunks]
chunk_embeddings = model.encode(chunk_texts, normalize_embeddings=True)
chunk_id_to_idx = {c["chunk_id"]: idx for idx, c in enumerate(chunks)}

corpus_tokens = [c["text"].lower().split() for c in chunks]
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

def retrieve_hybrid_candidates(query, top_k_dense=25, top_k_bm25=25, k_rrf=60):
    q_emb = model.encode([query], normalize_embeddings=True)[0]
    scores, indices = index.search(np.array([q_emb], dtype=np.float32), top_k_dense)
    dense_res = {chunks[idx]["chunk_id"]: rank + 1 for rank, idx in enumerate(indices[0]) if idx != -1}
    
    tokens = query.lower().split()
    bm25_scores = bm25.get_scores(tokens)
    bm25_top = np.argsort(bm25_scores)[::-1][:top_k_bm25]
    bm25_res = {chunks[idx]["chunk_id"]: rank + 1 for rank, idx in enumerate(bm25_top)}
    
    all_cids = set(dense_res.keys()).union(set(bm25_res.keys()))
    rrf_scores = {}
    for cid in all_cids:
        r_dense = dense_res.get(cid, 999)
        r_bm25 = bm25_res.get(cid, 999)
        rrf_scores[cid] = (1.0 / (k_rrf + r_dense) if r_dense != 999 else 0.0) + (1.0 / (k_rrf + r_bm25) if r_bm25 != 999 else 0.0)
        
    sorted_candidates = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return q_emb, sorted_candidates

def apply_mmr(q_emb, candidates, top_k=3, lambda_param=0.7):
    cand_cids = [c[0] for c in candidates]
    cand_scores = {c[0]: c[1] for c in candidates}
    
    # Normalize candidate scores to [0, 1]
    max_s = max(cand_scores.values()) if cand_scores else 1.0
    min_s = min(cand_scores.values()) if cand_scores else 0.0
    norm_scores = {cid: (cand_scores[cid] - min_s) / (max_s - min_s + 1e-12) for cid in cand_cids}
    
    selected_cids = []
    unselected = cand_cids.copy()
    
    while len(selected_cids) < top_k and unselected:
        best_cid = None
        best_mmr_score = -float('inf')
        
        for cid in unselected:
            relevance = norm_scores[cid]
            emb_cid = chunk_embeddings[chunk_id_to_idx[cid]]
            
            if not selected_cids:
                max_sim = 0.0
            else:
                sims = [float(np.dot(emb_cid, chunk_embeddings[chunk_id_to_idx[scid]])) for scid in selected_cids]
                max_sim = max(sims)
                
            mmr_score = lambda_param * relevance - (1.0 - lambda_param) * max_sim
            if mmr_score > best_mmr_score:
                best_mmr_score = mmr_score
                best_cid = cid
                
        selected_cids.append(best_cid)
        unselected.remove(best_cid)
        
    return selected_cids

def calculate_top3_diversity(selected_cids):
    if len(selected_cids) < 2:
        return 0.0
    embs = [chunk_embeddings[chunk_id_to_idx[cid]] for cid in selected_cids]
    sims = []
    for i in range(len(embs)):
        for j in range(i + 1, len(embs)):
            sims.append(float(np.dot(embs[i], embs[j])))
    # Average Pairwise Distance = 1 - Average Cosine Similarity
    avg_sim = float(np.mean(sims))
    return 1.0 - avg_sim

print("================================================================")
print("EVALUATING HYBRID RRF VS HYBRID RRF + MMR (lambda=0.7)")
print("================================================================")

no_mmr_hits = 0
mmr_hits = 0

no_mmr_diversities = []
mmr_diversities = []

for qitem in golden_set:
    q = qitem["question"]
    exp = qitem["expected"]
    
    q_emb, candidates = retrieve_hybrid_candidates(q)
    top3_no_mmr = [c[0] for c in candidates[:3]]
    top3_mmr = apply_mmr(q_emb, candidates, top_k=3, lambda_param=0.7)
    
    div_no_mmr = calculate_top3_diversity(top3_no_mmr)
    div_mmr = calculate_top3_diversity(top3_mmr)
    
    no_mmr_diversities.append(div_no_mmr)
    mmr_diversities.append(div_mmr)
    
    hit_no_mmr = (exp in top3_no_mmr) if exp else False
    hit_mmr = (exp in top3_mmr) if exp else False
    
    if hit_no_mmr: no_mmr_hits += 1
    if hit_mmr: mmr_hits += 1
    
    print(f"[{qitem['id']}] Question: {q[:45]}...")
    print(f"    RRF Top-3: {top3_no_mmr} | Hit? {hit_no_mmr} | Div: {div_no_mmr:.3f}")
    print(f"    MMR Top-3: {top3_mmr} | Hit? {hit_mmr} | Div: {div_mmr:.3f}")

valid_q = 10
print(f"\nNo MMR Hit-Rate@3: {no_mmr_hits}/{valid_q} ({no_mmr_hits/valid_q*100:.1f}%) | Avg Diversity: {np.mean(no_mmr_diversities):.3f}")
print(f"MMR (lambda=0.7) Hit-Rate@3: {mmr_hits}/{valid_q} ({mmr_hits/valid_q*100:.1f}%) | Avg Diversity: {np.mean(mmr_diversities):.3f}")
