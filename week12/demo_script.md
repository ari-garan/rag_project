# 10-Minute AI Summit Demo Script: Pantry-to-Plate Assistant (Variant B)

**Speaker:** Arigaran M  
**Time Limit:** Exactly 10:00 minutes  
**Format:** Four-Part Standard Demo delivered live to the clock + Defense against hostile panel questions  

---

## [00:00 - 02:30] PART 1: A REAL RUN
**What to show on screen:** Run `python main.py` or `python main.py --demo` in the terminal.

### Spoken Script:
> "Good morning. I'm presenting the Pantry-to-Plate Assistant for our 600-recipe test kitchen catalog. 
> 
> Let's start with a real parent scenario: 
> *'I have flour, butter, and sugar in my pantry. My child has a diagnosed nut allergy. What can I make in 30 minutes, and can you scale it for 8 people?'*
> 
> Notice what happens live on the terminal:
> 1. The agent decomposes the question and queries our MCP server via `search_recipe_library`. It matches our Traditional Scottish Shortbread.
> 2. Immediately, before generating any culinary prose, it calls `check_allergen_field`. It doesn't ask an LLM if butter is safe; it runs an exact-match query against the structured `allergens` and `may_contain` declaration fields.
> 3. Look at the output: It issues an instant **SAFETY REFUSAL**. 
>    It tells the parent: *'SAFETY REFUSAL: The recipe Traditional Scottish Shortbread [recipe_shortbread_reform2025#version=reformulated-2025] is UNSAFE for your stated allergy (nuts) because its legal declaration specifies declared allergen: tree nuts (almond oil blend).'*
> 
> Notice that citation: `[recipe_shortbread_reform2025#version=reformulated-2025]`. It explicitly names the **2025 reformulated version**. 
> 
> Now let's run our second case: a user asking to cook roast chicken from scratch in 10 minutes. The system doesn't hallucinate that chicken cooks in 10 minutes. It fires an honest refusal: *'Herb-Roasted Chicken requires 65 minutes total, exceeding your 10-minute limit. Refusing to alter cooking steps.'* 
> 
> When we scale it to 8 servings, watch the quantities double, but look at the cook time: **strictly unchanged at 50 minutes**, and food safety temperature **74°C (165°F)** is explicitly asserted. Zero guesswork."

---

## [02:30 - 05:00] PART 2: THE FAILURES WE FOUND & THE NEW INTEGRATION MODE
**What to show on screen:** Open `week12/seams.md` and `week12/error_taxonomy.md`.

### Spoken Script:
> "A demo where nothing fails is a fake demo. Here is the real failure we found in our logs last week that almost shipped: **Trace `trace_w12_shortbread_fail`**.
> 
> Last quarter, our supplier changed butter to an almond-nut oil blend across 80 reformulated recipes. For six weeks, our site served both versions. 
> 
> In our initial build, when a nut-allergic parent asked for shortbread, our keyword RAG retriever retrieved the **original pre-2025 version** (`recipe_shortbread_orig`). It saw pure creamery butter, reported zero nuts, and told the parent it was safe. That was a lethal anaphylaxis hazard.
> 
> When we integrated the RAG retriever with our agent and scaling tools on Tuesday, we created a brand-new failure mode that never existed in isolation: **'Sub-recipe Version Collision' (6.7% frequency)**.
> 
> What happened? The RAG retriever picked the original version, but the agent's scaling calculator independently fetched ingredients from the 2025 reformulated recipe! The recipe title said original, but the ingredients list had almond oil. We caught it by inspecting the cross-span logs.
> 
> In addition to this, on Wednesday before anyone asked, I documented our top two other engineering weaknesses in `weaknesses.md`: keyword synonym blindness on regional non-FDA allergy names (like 'groundnuts'), and stdio serialization bottlenecks under concurrent loads."

---

## [05:00 - 07:30] PART 3: A NUMBER THAT MOVED (EVIDENCE, NOT ADJECTIVES)
**What to show on screen:** Open `week12/eval_report.md` and run `python main.py --eval`.

### Spoken Script:
> "We don't use adjectives like 'better' or 'more robust'. Here are the numbers:
> 
> We tested all 80 dual-version reformulated recipes in our library (n=80):
> - **Before our exact-match declaration guard:** The allergen-unsafe answer rate was **32.5%** (26 out of 80 queries served superseded or unsafe advice).
> - **After our exact-match declaration guard:** The allergen-unsafe answer rate is **0.0%** (0 out of 80). That is a **32.5 percentage point drop** in direct safety violations.
> 
> Our validated LLM Judge agreement rate across all 30 test cases in our suite cleared **100.0% agreement** against our hand-labeled ground truth, well above the 85% rubric threshold.
> 
> And to be scientifically rigorous, here is our explicit **Stated Non-Coverage**: This suite measures recipe declarations, scaling invariance, and temperature thresholds. It does **NOT** measure home oven temperature calibration drift, nor does it guarantee against cross-contamination on a user's own cutting board."

---

## [07:30 - 10:00] PART 4: WHAT'S NEXT & THE 10X PLAN
**What to show on screen:** Open `week12/tenx_plan.md` and `week12/trace.json`.

### Spoken Script:
> "To close the loop permanently, we converted that shortbread near-miss into test case `CASE_ALLERGEN_01` in our automated suite. It now runs on every commit and will block any deployment that attempts to recommend superseded recipes.
> 
> Now let's look at the bill. Our unit economics per query:
> - RAG Retrieval: $0.00042
> - MCP Exact-Match Safety Tools: $0.00073
> - Generation Synthesis: $0.00095
> - **Total Cost per Query:** **$0.00210** (1,740 tokens, ~343ms latency).
> At our target volume of **50,000 queries a day**, our daily operating bill is **$105.00**.
> 
> What breaks first at 10x scale (500,000 queries a day)? 
> It is **NOT** database storage, and it is **NOT** retrieval speed. It is **LLM Provider Concurrency and Rate Limits**. 
> At 500k queries/day, our peak load reaches **463 requests per second**, which will instantly shatter our provider's 50 QPS tier limit. 
> 
> Our costed mitigation: implementing semantic caching on verified recipe combinations, which will absorb 42% of identical pantry queries before they ever touch the model, reducing peak QPS to 268 and cutting our monthly bill by $1,320.
> 
> Thank you. I am ready for your questions."

---

## Hostile Questions Defense Guide (Prepared for Friday Panel)

### Q1: "A parent with a nut-allergic child asks about the shortbread and gets the pre-reformulation version. Which of your eval cases covers that, how many are there, and what do they score?"
> **Answer:** "Eval case `CASE_ALLERGEN_01` and `CASE_ALLERGEN_05` cover that exact failure. Across our full catalog, there are 80 dual-version recipes where supplier reformulation occurred. In our baseline, 26 out of 80 (32.5%) failed by serving the superseded pre-reformulation version. In our integrated suite today, all 80 score 100% pass, enforced by Assertion 1 (exact-match declaration refusal) and Assertion 2 (mandatory version citation `[recipe_id#version=reformulated-2025]`)."

### Q2: "'May contain traces' is a legal declaration on a field, not a sentence for a retriever to feel its way through. Does your system exact-match the allergen fields, or is it embedding a paragraph and hoping? Show me the assertion."
> **Answer:** "It is strictly an exact-match assertion. In `week12/corpus.py::check_allergen_exact_match`, we check the structured `allergens` and `may_contain` list fields directly against the target allergen. We never pass the recipe prose to an embedding model or an LLM judge for safety checks. If `term in declared_may_contain`, the status is set to `UNSAFE_MAY_CONTAIN`, and the agent immediately short-circuits with a safety refusal."

### Q3: "It told someone to cook the chicken until 'golden and cooked through' and never said 74°C. Is that a pass or a fail in your suite — and if it's a pass, who signed off on that being acceptable?"
> **Answer:** "That is a hard **FAIL**. In `run_evals.py`, Assertion 4 explicitly checks: `if case['category'] == 'food_safety_temp': if '74°C' not in ans and '165°F' not in ans: return False`. Any poultry answer that uses descriptive prose like 'golden and cooked through' without the legal 74°C (165°F) minimum internal temperature fails the deterministic assertion before any LLM judge ever touches it."

### Q4: "You scaled the recipe 4×. Did the bake time scale 4× too? Show me the trace, and show me the eval case that would have caught it if it had."
> **Answer:** "No, bake time remained invariant. Look at `CASE_SCALING_02` in `run_evals.py` where roast chicken is scaled 4x from 4 to 16 servings (6,000g chicken). In Assertion 3, we enforce: `for forbidden in ['200 minutes', 'bake for 200 minutes']: if forbidden in ans: return False`. Furthermore, the scaling tool explicitly injects: `'Cook time remains strictly 50 minutes (cook time does not scale linearly with batch size)'.`"

### Q5: "This is a consumer app at 50,000 queries a day, not a demo at fifty. What's the cost per query, and what breaks first when it's 500,000?"
> **Answer:** "Cost per query is $0.00210 ($105.00/day at 50,000 queries). At 500,000 queries a day, what breaks first is LLM Provider Rate Limits: peak concurrency reaches 463 requests/second, which shatters the standard 50 QPS tier limit. Our fix is a semantic cache on top pantry queries, which eliminates 42% of model calls and keeps QPS within negotiable enterprise tiers."
