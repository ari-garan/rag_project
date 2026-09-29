# Injection Test: Allergen Worker 500 Error

**Scenario:** We injected a hard 500 error into the Allergen/Nutrition worker during the resolution of Case Q2 (Biryani spices).

**Orchestrator's Actual Behaviour:** 
DEGRADE: The orchestrator caught the 500 error, skipped the allergen check, and degraded gracefully to a partial answer, stating "Allergen data currently unavailable" alongside the recipe. It did not retry endlessly, and crucially, it did not lie by hallucinating allergen safety.
