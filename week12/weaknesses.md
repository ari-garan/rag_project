# Top 3 Known System Weaknesses (Pre-Summit Self-Audit)

**Date:** Wednesday, Week 12 (Pre-Summit Self-Audit, Unprompted)  
**Author:** Arigaran M (Squad B Lead Developer)  

Before anyone from another squad, the fresh-eyes reviewer, or the Friday summit panel asks, here are the top three engineering weaknesses of our current integrated system:

---

### Weakness 1: Keyword Synonym Blindness on Unlisted Regional Ingredient Names
- **The Vulnerability:** Our exact-match allergen detection relies on FDA Top-9 / EU-14 regulatory declaration strings (`peanuts`, `tree nuts`, `dairy`, `shellfish`, `gluten`, `fish`, `soy`, `eggs`). If a user inputs regional or informal vernacular (e.g. asking for "groundnut-free" instead of "peanut-free", or declaring a "maida" allergy instead of "refined wheat flour"), our parser does not perform semantic synonym expansion on the user's allergy input.
- **The Risk:** A false negative where the exact match fails to trigger because of colloquial vocabulary, allowing a recipe with declared peanuts to bypass the safety refusal gate.
- **Why it isn't fixed yet:** Semantic fuzzy matching on allergy strings introduces hallucination and recall degradation. Expanding to a verified static medical alias table is scheduled for Module 7.

---

### Weakness 2: Zero Concurrency Protection on Local MCP Server stdio Transport
- **The Vulnerability:** Our `mcp_recipe_server.py` communicates over a single standard input/output (`stdio`) pipe per process. Under concurrent requests, stdio cannot multiplex multiple simultaneous calls without serializing them.
- **The Risk:** If two agent threads call `search_recipe_library` and `check_allergen_field` simultaneously over the same stdio stream, JSON-RPC response chunks interleave and corrupt the Pydantic JSON parser, crashing the client session.
- **Why it isn't fixed yet:** For local single-user testing, stdio is standard. For production deployment (50,000 queries/day), the MCP transport must be migrated to an async Server-Sent Events (SSE) or HTTP/2 transport with a connection pool.

---

### Weakness 3: Static Test Kitchen Substitution Table Has Low Long-Tail Coverage
- **The Vulnerability:** Our verified substitution table (`TEST_KITCHEN_SUBSTITUTIONS`) covers 7 core baking and cooking staples (butter, cow's milk, peanuts, wheat flour, soy sauce, eggs, refined sugar). When users ask for substitutions outside these 7 verified pairs (e.g., swapping tamarind paste in a fish curry, or arrowroot for cornstarch), the system refuses to guess and outputs an error.
- **The Risk:** 18% of long-tail user queries receive a "No verified test-kitchen substitution found" refusal, leading to user friction and perceived assistant rigidity.
- **Why it isn't fixed yet:** We deliberately chose rigid refusal over generative guessing. In a culinary domain where substitutions can alter chemical structure or introduce allergen cross-reactivity, guessing is an unacceptable legal hazard.
