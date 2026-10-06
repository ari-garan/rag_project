import time
from tools import search_recipes, scale_ingredients, get_allergen_substitute, DietRestriction

def allergen_worker(allergen, diet, force_500=False):
    # Worker simulates thinking
    time.sleep(0.1)
    
    if force_500:
        return "ERROR 500: Allergen Worker Offline", 150
        
    sub = get_allergen_substitute(allergen, DietRestriction(diet))
    return sub, 150

def substitution_worker(current_recipe, sub):
    time.sleep(0.1)
    if "Warning" in sub:
        return current_recipe, 150 # Cascade warning
    return current_recipe + f" | Final Swap: {sub}", 150

def run_orchestrator(recipe_name, servings, allergen, diet, force_500=False):
    start = time.time()
    tokens = 0
    
    # 1. Orchestrator Initial Planning
    time.sleep(0.1)
    tokens += 600
    
    # Get recipe
    current_recipe = search_recipes(recipe_name)
    current_recipe = scale_ingredients(current_recipe, servings)
    
    # 2. Hand-off to Allergen Worker (Context Re-send Bloat)
    time.sleep(0.1) # Orchestrator packaging context
    tokens += 3800 # Orchestrator passes entire corpus to worker
    
    sub_result, worker_tokens = allergen_worker(allergen, diet, force_500=force_500)
    tokens += worker_tokens
    
    if force_500:
        # Orchestrator Degrades gracefully
        current_recipe += " | Note: Allergen data currently unavailable."
        time.sleep(0.1)
        tokens += 660 # Synthesis
        return current_recipe, tokens, tokens * 0.0001, time.time() - start, "DEGRADE"
        
    # 3. Hand-off to Substitution Worker
    time.sleep(0.1)
    tokens += 4100 # Passing full recipe and allergen notes
    
    final_recipe, sub_tokens = substitution_worker(current_recipe, sub_result)
    tokens += sub_tokens
    
    # 4. Orchestrator Synthesis
    time.sleep(0.1)
    tokens += 660
    
    return final_recipe, tokens, tokens * 0.0001, time.time() - start, "SUCCESS"

if __name__ == "__main__":
    res, tok, cost, lat, status = run_orchestrator("Thai Curry", 4, "peanuts", "nut_free")
    print(f"Orchestrator Result: {res}\nTokens: {tok}, Cost: ${cost:.4f}, Latency: {lat:.3f}s, Status: {status}")

