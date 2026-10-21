# Pantry-to-Plate Assistant (Week 12 Capstone - Variant B)

> **M6 Capstone Portfolio Piece:** A production-grade, observable culinary assistant combining 11 weeks of RAG, hand-built agent loops, live Model Context Protocol (MCP) tool discovery, exact-match allergen safety, and per-request span logging.

---

## Quickstart: Stranger Guide (Zero to Working Answer in One Command)

No complex environment setup or external GPU required. Run with standard Python:

### 1. Run the Live 4-Part Summit Demo (Recommended for Evaluation)
```powershell
python main.py --demo
```
*Delivers the complete four-part summit presentation live to the clock: Real Run -> Failures Found -> A Number That Moved -> 10x Scale Plan.*

### 2. Run the Full 30-Case Integrated Evaluation Suite
```powershell
python main.py --eval
```
*Executes all 30 deterministic assertions and LLM Judge evaluations across 6 categories in ~5 seconds.*

### 3. Ask a Custom Cooking / Pantry Question
```powershell
python main.py --query "I have flour, butter, and sugar. Can I make traditional shortbread?" --allergy "nuts" --servings 8
```

### 4. Interactive Pantry Mode
```powershell
python main.py
```

---

## Capstone Artifacts & Submission Checklist (`week12/`)

All capstone deliverables required by the M6 House Rubric are located in [`week12/`](week12/):

| Deliverable File | Description & Rubric Evidence |
| :--- | :--- |
| **[`main.py`](main.py)** | **Single Entry Point:** Runs app, eval suite, and 4-part demo from one command. |
| **[`week12/seams.md`](week12/seams.md)** | **Tuesday's Unedited Seam List:** 8 integration seams audit marked fixed, accepted, or deferred. |
| **[`week12/architecture.md`](week12/architecture.md)** | **One-Page Architecture Sketch:** Mermaid flowchart, host LLM isolation, and cost breakdown per span. |
| **[`week12/eval_report.md`](week12/eval_report.md)** | **Eval Suite Output:** 30 cases (100% pass), n=80 reformulation drop (32.5% -> 0.0%), 100% judge agreement, stated non-coverage. |
| **[`week12/weaknesses.md`](week12/weaknesses.md)** | **Top 3 Known Weaknesses:** Dated Wednesday, unprompted (synonym blindness, stdio concurrency, long-tail swaps). |
| **[`week12/demo_script.md`](week12/demo_script.md)** | **10-Minute Demo Script:** Four-part standard script + answers to all 5 hostile panel questions. |
| **[`week12/error_taxonomy.md`](week12/error_taxonomy.md)** | **Re-Scored Error Taxonomy:** 6 ranked modes with trace IDs; includes NEW integration mode ('Sub-recipe Version Collision'). |
| **[`week12/trajectory_eval.md`](week12/trajectory_eval.md)** | **Trajectory Evaluation:** 12 cases, tool-choice accuracy 91.7%, outcome-vs-trajectory gap 16.7% (2 right-answer-wrong-path traces). |
| **[`week12/trace.json`](week12/trace.json)** | **End-to-End Trace:** Single `trace_id` intact across agent and MCP hops, latency/cost per span, PII health data hashed. |
| **[`week12/tenx_plan.md`](week12/tenx_plan.md)** | **10x Engineering Plan:** $0.00210 cost/query ($105/day @ 50k); identifies LLM concurrency limits breaking first at 500k queries/day. |
| **[`week12/fresh_eyes.md`](week12/fresh_eyes.md)** | **Fresh-Eyes Review Note:** External squad review (Jordan Chen, Squad C), where they stumbled, and changes made. |
| **[`week12/bonus_substitution_eval.md`](week12/bonus_substitution_eval.md)** | **Bonus Challenge:** Allergen safety through substitution chain; red before, green after on secondary allergen introduction. |

---

## Core System Architecture

```text
[User Query + Allergy]
       │
       ▼
 [main.py Gateway] ───► [Host Agent Orchestrator] ◄──► [MCP Recipe & Safety Server]
                             │                                 ├── search_recipe_library
                             │ (Single trace_id surviving)     ├── check_allergen_field (EXACT-MATCH)
                             │                                 ├── scale_recipe_batch (Invariant cook time)
                             │                                 ├── get_safe_internal_temp (74°C poultry)
                             │                                 └── get_kitchen_substitution
                             ▼
               [Deterministic Assertion Engine]
                    ├── Unsafe ──► Immediate Safety Refusal (Zero Token Waste)
                    └── Safe   ──► Host Synthesis Call (Prompt Versioned)
                             │
                             ▼
           [capstone_traces.jsonl] (PII Hash + Cost/Latency per Span)
                             │
                             ▼
    [User Response with Mandatory Version Citation [recipe_id#version=...]]
```

---

## Kitchen Reality Safeguards Enforced
1. **Exact-Match Allergen Declarations:** Never infers allergen safety from prose. Evaluates structured `allergens` and `may_contain` fields.
2. **Versioned Citations:** Mandatory citation of recipe ID and formulation version (`reformulated-2025` vs `original`). Prevents citing superseded recipes.
3. **Cook-Time Invariant Scaling:** Scaling batch quantities 4x scales grams/milliliters linearly, but preserves bake/cook time.
4. **Internal Safety Temperatures:** Poultry dishes strictly assert minimum internal temperature of **74°C (165°F)**.
5. **PII Health Line Held:** User dietary health declarations are salted and hashed (SHA-256) before trace persistence.
