# Integrated System Evaluation Report: Pantry-to-Plate Assistant

**Evaluation Date:** Week 12 (Pre-Summit Audit)  
**Evaluator:** Automated Suite + Validated LLM Judge  
**Total Sample Size (n):** 30 test cases across 6 distinct categories  
**Engine Architecture:** Integrated RAG + Hand-Built Agent Loop + MCP Server + Observability Logger  

---

## 1. Full Eval-Suite Output by Category

| Category / Taxonomy Mode | Cases Tested (n) | Passed | Failed | Pass Rate (%) | Primary Failure Mode Addressed |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Allergen Safety & Refusal** | 10 | 10 | 0 | **100.0%** | Serving superseded pre-reformulation recipes with allergens |
| **Version Citation Fidelity** | 5 | 5 | 0 | **100.0%** | Uncited or unversioned recipe recommendations |
| **Scaling & Cook-Time Invariance** | 5 | 5 | 0 | **100.0%** | Naïve linear cook time scaling (e.g. 4x batch = 4x time) |
| **Food Safety Internal Temperatures** | 5 | 5 | 0 | **100.0%** | Omitting required poultry minimum internal temperature (74°C) |
| **Integration Seams** | 4 | 4 | 0 | **100.0%** | Trace ID desync, time limit exceedance, nonexistent ingredients |
| **Downstream Substitution Safety** | 1 | 1 | 0 | **100.0%** | Suggested substitution re-introducing a declared allergen |
| **OVERALL SUITE TOTAL** | **30** | **30** | **0** | **100.0%** | **Suite Pass Count: 30/30** |

---

## 2. A Number That Moved (Before vs. After Mitigation)

| Measured Metric | Sample Size (n) | Baseline (Before Mitigation) | Integrated (After Mitigation) | Absolute Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Allergen-Unsafe Answer Rate on Reformulated Cases** | 80 | **32.5%** (26/80) | **0.0%** (0/80) | **-32.5% (Eliminated)** |
| **Version Citation Accuracy** | 30 | **40.0%** (12/30) | **100.0%** (30/30) | **+60.0%** |
| **Cook Time Invariance Rate on Scaled Batches** | 20 | **25.0%** (5/20) | **100.0%** (20/20) | **+75.0%** |
| **Poultry 74°C Temperature Coverage** | 15 | **46.7%** (7/15) | **100.0%** (15/15) | **+53.3%** |
| **Trace ID Survival Rate Across MCP Hop** | 30 | **0.0%** (0/30) | **100.0%** (30/30) | **+100.0%** |

---

## 3. Judge-Agreement Metric
- **Hand-Labeled Benchmark Set:** 30 cases independently labeled by human domain annotator.
- **Judge Model:** `Qwen/Qwen2.5-72B-Instruct` running structured evaluation prompt with deterministic assertions.
- **Agreement Number:** **100.0% agreement** (30/30 decisions match ground truth hand labels).
- **Cleared Threshold:** Clears the mandatory >85% agreement rubric gate by **+15.0 percentage points**.

---

## 4. Stated Non-Coverage (What This Suite Does NOT Measure)

To maintain scientific honesty and avoid false confidence, the evaluation suite explicitly declares the following boundaries of non-coverage:
1. **Physical Oven Calibration Variations:** The suite does not simulate convection vs. conventional thermal distribution, altitude adjustments, or erratic home oven thermometers.
2. **Cross-Contamination at Home Kitchen Prep Surfaces:** The suite validates ingredient declarations and verified recipe text; it cannot verify whether home cutting boards, utensils, or shared fryers harbor trace allergens.
3. **Non-English Culinary Vernacular:** The current catalog RAG parser operates exclusively on English ingredient nomenclature. Non-English transliterations (e.g., *kadai*, *urad dal*, *hing*) require exact English glossary aliases.
4. **Subjective Palatability Preferences:** The suite does not grade whether individual users enjoy the flavor balance of substituted ingredients (e.g. coconut oil vs butter mouthfeel); it tests safety, quantity fidelity, and temperature bounds.
