# Week 12 Capstone Deliverables (Variant B: Pantry-to-Plate Assistant)

This directory contains the complete integration, evaluation suite, and defense artifacts for the Week 12 Capstone.

## Quick Execution
- **Run Evaluation Suite:** `python ../main.py --eval` or `python run_evals.py`
- **Run Live Demo:** `python ../main.py --demo`
- **Interactive Mode:** `python ../main.py`

## Deliverables Index
1. `corpus.py` — 600-recipe library with 80 dual-version reformulated pairs, structured allergen declarations, and test kitchen tables.
2. `mcp_recipe_server.py` — FastMCP server exposing recipe search, exact-match allergen assertions, scaling, and safe temperatures.
3. `mcp_config.json` — MCP client discovery configuration.
4. `pantry_assistant.py` — Integrated agent loop with RAG, MCP discovery, span logging, and PII protection.
5. `run_evals.py` — 30-case evaluation suite with assertions before judges.
6. `seams.md` — Tuesday's unedited seam list marked fixed/accepted/deferred.
7. `architecture.md` — One-page architecture diagram with model calls and financial spend per span.
8. `eval_report.md` — Full evaluation report with n, pass rates, judge agreement, and stated non-coverage.
9. `weaknesses.md` — Top 3 known weaknesses dated Wednesday, unprompted.
10. `demo_script.md` — 10-minute demo script (4-part standard) and hostile question defense.
11. `error_taxonomy.md` — Re-scored error taxonomy with frequencies and the new integration mode.
12. `trajectory_eval.md` — Trajectory eval over 12 cases with outcome-vs-trajectory gap.
13. `trace.json` — End-to-end trace with per-span latency/cost and PII hash.
14. `tenx_plan.md` — Unit economics ($0.00210/query) and 10x scale plan (500k queries/day).
15. `fresh_eyes.md` — External squad review note from Squad C.
16. `bonus_substitution_eval.md` — Bonus challenge: Allergen safety through the substitution chain.
