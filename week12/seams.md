# Tuesday's Unedited Seam List (Pre-Summit Integration Audit)

Date: Tuesday, Week 12
Auditor: Arigaran M (Squad B - Recipes & Food)
Status Legend:
- [FIXED]: Resolved through code, assertion, or protocol change
- [ACCEPTED]: Known behavior accepted under stated risk tolerances
- [RAN-OUT-OF-TIME]: Deferred to post-capstone production backlog

---

### Seam 1: RAG Retriever <-> Agent Boundary [Version Collision]
- **Location:** `week12/corpus.py` <-> `week12/pantry_assistant.py`
- **What happened:** When the user asked for traditional shortbread, the keyword RAG retriever returned the original pre-2025 version (`recipe_shortbread_orig`), but the test kitchen scaling tool loaded the 2025 reformulated recipe (`recipe_shortbread_reform2025`). This created an acute version collision: the system cited a nut-free recipe while baking with nut-oil butter!
- **Status:** **[FIXED]**
- **Resolution:** Added strict `version_preference="reformulated-2025"` filtering and mandatory version citation formatting `[recipe_id#version=...]` validated by deterministic Assertion 2.

---

### Seam 2: Agent <-> MCP Transport Boundary [Schema & Serialization Desync]
- **Location:** `week12/pantry_assistant.py` <-> `week12/mcp_recipe_server.py`
- **What happened:** When calling `check_allergen_field` over stdio JSON-RPC, boolean values (`True`/`False`) returned as JSON strings (`"true"`) in FastMCP responses, causing the agent's Python `if result.get("is_safe"):` check to evaluate `"false"` as truthy!
- **Status:** **[FIXED]**
- **Resolution:** Enforced explicit schema normalization: all MCP safety tools return typed status codes (`SAFE`, `UNSAFE_DECLARED`, `UNSAFE_MAY_CONTAIN`) instead of raw un-namespaced booleans.

---

### Seam 3: Scaling Tool <-> Cook Time Preserving Boundary [Linear Over-scaling]
- **Location:** `week12/corpus.py::scale_recipe_quantities`
- **What happened:** Initial naïve agent implementation scaled all recipe numbers by the batch multiplier, multiplying the 50-minute roast chicken cook time to 200 minutes when scaling to 16 servings!
- **Status:** **[FIXED]**
- **Resolution:** Decoupled ingredient scaling from thermal dynamics. Cook time and bake time are strictly immutable constants regardless of serving multiplier (`cook_time_scaled = False`).

---

### Seam 4: Observability Trace ID Propagation <-> MCP Hop [Trace Loss]
- **Location:** `week12/pantry_assistant.py` span logger
- **What happened:** The initial span logger generated a new UUID inside the MCP server process, losing the parent agent's `trace_id`. Tracing a single user request required correlating timestamps across disconnected logs.
- **Status:** **[FIXED]**
- **Resolution:** Propagated `trace_id` as a first-class parameter across all MCP tool calls and structured span records, preserving a single trace identifier from question-in to answer-out.

---

### Seam 5: Allergen Logging <-> PII Data Privacy Boundary [Health Data Leak]
- **Location:** `week12/capstone_traces.jsonl`
- **What happened:** Raw user health declarations (e.g. "my 4-year-old has severe peanut anaphylaxis") were initially written directly into unencrypted log files. Under HIPAA/GDPR Article 9, dietary health conditions constitute special category data.
- **Status:** **[FIXED]**
- **Resolution:** Implemented `_anonymize_pii_health_data()`: user allergies are salted and hashed with SHA-256 (`sha256:...`) before disk persistence. The agent reasons on memory state only.

---

### Seam 6: Downstream Substitution <-> Secondary Allergen Trap [Cascade Blindness]
- **Location:** `week12/corpus.py::TEST_KITCHEN_SUBSTITUTIONS`
- **What happened:** A user asked for a dairy-free swap for butter. The system proposed almond-oil butter blend. Because the recipe was originally nut-free, the agent approved the dish—blind to the fact that its own proposed substitution introduced tree nuts to a nut-allergic child!
- **Status:** **[FIXED]** (Bonus Challenge Closed Loop)
- **Resolution:** Moved allergen verification downstream of substitution synthesis. The recipe is re-checked AS SUBSTITUTED, triggering an immediate `REFUSAL_ALLERGEN_UNSAFE`.

---

### Seam 7: Multilingual Culinary Synonym Handling [Vocabulary Gap]
- **Location:** `week12/corpus.py::check_allergen_exact_match`
- **What happened:** If a user specifies "groundnuts" instead of "peanuts", or "clarified butter" instead of "ghee", exact string matching without synonym expansion could miss the declaration.
- **Status:** **[ACCEPTED]**
- **Risk Tolerance:** Test kitchen allergen fields conform to the FDA Top-9 / EU-14 regulatory naming standards. System prompt instructs users to declare standard allergen categories.

---

### Seam 8: Live Vector Index Re-embedding During Catalog Updates
- **Location:** FAISS / SentenceTransformer Index Pipeline
- **What happened:** Re-embedding the 600-recipe catalog on local Windows machines triggered Application Control DLL blocks (`torch_global_deps.dll`).
- **Status:** **[RAN-OUT-OF-TIME]**
- **Mitigation:** Deployed deterministic tokenized lexical RAG search with version prioritization for the capstone release. Scheduled cloud-based async vector re-indexing for Module 7 production sprint.
