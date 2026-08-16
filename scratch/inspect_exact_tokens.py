import os
import pickle

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta_path = os.path.join(base_dir, 'vector_store', 'metadata.pkl')

with open(meta_path, 'rb') as f:
    meta = pickle.load(f)

chunks = meta['chunks']

def search_text(kw):
    print(f"=== KEYWORD: {kw} ===")
    for c in chunks:
        if kw.lower() in c['text'].lower():
            safe_text = c['text'].encode('ascii', 'replace').decode('ascii')
            print(f"[{c['chunk_id']}] Page {c['pages']}: {safe_text[:200]}...")
            print("-" * 40)

search_text("oven")
search_text("bake")
search_text("400")
search_text("350")
search_text("450")
search_text("fenugreek")
search_text("asafoetida")
search_text("cardamom")
search_text("star anise")
search_text("nutmeg")
