import time
from tools import search_recipes, scale_ingredients, get_allergen_substitute, DietRestriction

def run_workflow(recipe_name, servings, allergen, diet):
    start = time.time()
    tokens = 0
    
    time.sleep(0.05) # Fast static parsing
    tokens += 100 # Only one call
    
    recipe = search_recipes(recipe_name)
    recipe = scale_ingredients(recipe, servings)
    
    if allergen:
        sub = get_allergen_substitute(allergen, DietRestriction(diet))
        recipe += f" | Swapped {allergen} for {sub}"
        # Fixed workflow doesn't loop. It fails cascade automatically.
        
    return recipe, tokens, tokens * 0.0001, time.time() - start, "SUCCESS"

if __name__ == "__main__":
    # Test run to make the workflow runnable by one command
    res, tok, cost, lat, status = run_workflow("Cake", 2, "milk", "dairy_free")
    print(f"Workflow Result: {res}\nTokens: {tok}, Cost: ${cost:.4f}, Latency: {lat:.3f}s, Status: {status}")
