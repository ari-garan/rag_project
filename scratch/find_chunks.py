import os
import pickle

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta_path = os.path.join(base_dir, 'vector_store', 'metadata.pkl')

with open(meta_path, 'rb') as f:
    meta = pickle.load(f)

chunks = meta['chunks']

print(f"Total chunks: {len(chunks)}")

def search_term(term):
    print(f"\n=================== SEARCH: {term} ===================")
    matches = [c for c in chunks if term.lower() in c['text'].lower()]
    print(f"Found {len(matches)} matches")
    for c in matches[:3]:
        safe_text = c['text'].encode('ascii', 'replace').decode('ascii')
        print(f"[{c['chunk_id']}] Pages {c['pages']}:")
        print(safe_text)
        print("-" * 50)

search_term("asafoetida")
search_term("fenugreek")
search_term("400")
search_term("350")
search_term("bisi bele")
search_term("avial")
search_term("kodi vepudu")
search_term("eral thokku")
search_term("chicken 65")
search_term("mysore pak")
search_term("xanthan")
search_term("air fryer")
