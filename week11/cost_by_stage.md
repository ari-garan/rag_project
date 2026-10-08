# Cost per Query by Stage (Trace req-998f4-2026)

* **Retrieval (Vector DB):** $0.0000 (Self-hosted FAISS, no API cost)
* **Tools / Allergen API:** $0.0005 (Fixed rate API call)
* **Generation (LLM):** $0.0018 (1205 in / 45 out tokens)
* **Total Cost Per Query:** $0.0023

*Optimization Note:* Generation dominates 78% of the cost. Adding a semantic cache for common dietary substitution questions would drop the generation cost to $0.0000 on cache hits.
