# Re-Scored Error Taxonomy: Integrated Pantry-to-Plate Assistant

**Evaluation Population:** 30 comprehensive integration test traces + 80 baseline reformulation audit traces  
**Scoring Date:** Week 12 Capstone Audit  

---

## Ranked Failure Taxonomy Table

| Rank | Failure Mode (Plain Language) | Origin | Frequency (Baseline) | Frequency (Integrated) | Severity | Example Trace ID |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **1** | **Allergen Safety & Supplier Reformulation Near-Miss**<br>Serves pre-2025 version containing unflagged allergens (e.g. shortbread nut-oil blend). | Inherited from Week 5 | 32.5% (26/80) | **0.0%** (0/80) | **Poisons (Fatal)** | `trace_w12_shortbread_fail` |
| **2** | **Linear Cook-Time Over-scaling**<br>Scaling serving count linearly multiplies oven bake time (e.g. 50 min roast chicken becomes 200 min). | Inherited from Week 5 | 25.0% (5/20) | **0.0%** (0/20) | **Ruins Dish** | `trace_w12_scale_fail` |
| **3** | **Food Safety Poultry Temperature Omission**<br>Advises cooking poultry until 'golden' without legal 74°C (165°F) minimum internal temperature. | Inherited from Week 5 | 20.0% (3/15) | **0.0%** (0/15) | **Poisons (Salmonella)** | `trace_w12_temp_fail` |
| **4** | **Sub-recipe Version Collision**<br>*(NEW - CREATED BY INTEGRATION)*<br>RAG retriever selects original recipe ID while Agent scaling tool queries 2025 reformulated ingredients table, creating an incompatible Frankenstein recipe. | **NEW (Integration)** | 6.7% (2/30) | **0.0%** (0/30) | **Poisons** | `trace_w12_version_collision` |
| **5** | **Downstream Substitution Allergen Cascade**<br>*(NEW - CREATED BY INTEGRATION)*<br>Agent suggests a dairy-free butter swap that introduces tree nuts, poisoning a nut-allergic child on a previously safe recipe. | **NEW (Integration)** | 3.3% (1/30) | **0.0%** (0/30) | **Poisons (Fatal)** | `trace_w12_downstream_swap_trap` |
| **6** | **Long-Tail Unverified Substitution Rejection**<br>Refuses to guess culinary substitutions outside the 7 test-kitchen verified staple ingredients. | System Design Choice | 13.3% (4/30) | **13.3%** (Accepted) | **User Friction** | `trace_w12_sub_rejection` |

---

## Detailed Analysis of Mode Created by Integration

### Mode 4: Sub-recipe Version Collision (`trace_w12_version_collision`)
- **How Integration Created It:** In Week 4, the RAG retriever ran in isolation, returning top-k text chunks based on semantic similarity. In Week 7, the Agent scaling tool ran in isolation, taking recipe IDs and multiplying numbers. When wired together behind the single entry point, the RAG retriever matched `recipe_shortbread_orig` because its title matched the user's keywords, but the Agent's scaling tool fetched the newest ingredients from `recipe_shortbread_reform2025`.
- **The Result:** The system generated an answer that cited the original recipe, claimed it was nut-free, but listed the 2025 ingredients containing almond-oil butter blend!
- **The Mitigation:** Enforced single-source version resolution: the MCP retriever returns the canonical recipe record with an immutable `version` tag. Downstream scaling and allergen tools accept this version context and cannot query out-of-sync ingredient records.
