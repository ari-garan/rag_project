# Week 12 Trajectory Evaluation: Outcome vs. Trajectory Gap Analysis

**Evaluated Entity:** Integrated Pantry-to-Plate Agent (`week12/pantry_assistant.py`)  
**Sample Size:** 12 representative cooking requests with dietary and scaling constraints  
**Trajectory Ground Truth:** Standard execution graph: `[search_recipe_library]` -> `[check_allergen_field]` -> `[scale_recipe_batch]` -> `[get_safe_internal_temp]` -> `[synthesis]`  

---

## 1. Outcome vs. Trajectory Gap Metric

| Metric | Score | Detail |
| :--- | :---: | :--- |
| **Outcome Pass Rate** | **100.0%** (12/12) | 12 out of 12 requests delivered factually accurate, allergen-safe answers |
| **Trajectory Pass Rate** | **83.3%** (10/12) | 10 out of 12 requests adhered strictly to the mandatory tool execution order |
| **THE GAP NUMBER** | **16.7%** (2 cases) | **Outcome pass rate exceeds trajectory pass rate by 16.7 percentage points** |

> **Why the Gap Matters:** A 16.7% gap is the honest number. It reveals that in 2 cases, the agent delivered the *right answer via the wrong path*. It arrived at a safe conclusion through serendipity or latent model bias rather than following the mandatory safety verification tool chain. In high-stakes allergen safety, a right answer on an unverified path is a latent defect.

---

## 2. Right-Answer-Wrong-Path Trace Deconstruction

### Trace 1: `trace_w12_traj_skip1` (Request: "Quick coconut yellow dal, peanut allergy")
- **Expected Trajectory:** `search_recipe_library("yellow dal")` -> `check_allergen_field("recipe_quick_dal", "peanuts")` -> `synthesis`
- **Actual Trajectory Taken:** `search_recipe_library("yellow dal")` -> `synthesis` *(SKIPPED `check_allergen_field`)*
- **Outcome:** PASS. The answer correctly affirmed that yellow split moong dal does not contain peanuts.
- **The Defect:** The agent omitted the structured declaration check because yellow dal seemed 'obviously safe' from its title. While true for this recipe, skipping the tool on other dal formulations (e.g. South Indian dals tempered with peanut oil) would result in a fatal poisoning.

### Trace 2: `trace_w12_traj_skip2` (Request: "Roast chicken for egg-allergic guest")
- **Expected Trajectory:** `search_recipe_library` -> `check_allergen_field(allergen="egg")` -> `get_safe_internal_temp` -> `synthesis`
- **Actual Trajectory Taken:** `search_recipe_library` -> `get_safe_internal_temp` -> `synthesis` *(SKIPPED `check_allergen_field`)*
- **Outcome:** PASS. Chicken with rosemary contains no eggs.
- **The Defect:** The agent inferred safety from ingredient names rather than asserting against the structured field, violating legal safety compliance.

---

## 3. Integrated Trajectory Performance Metrics

- **Tool-Choice Accuracy:** **91.7%** (44 correct tool selections out of 48 opportunities)
- **Tool Argument Validity Rate:** **100.0%** (0 hallucinated recipe IDs or invalid parameter types across all runs)
- **Step Efficiency:** **0.92** (average actual steps / optimal steps)
- **Tool-Looping Incidents:** **0** (no infinite retries or repetitive allergen lookups)
