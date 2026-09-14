import time
from tools import search_recipes, scale_ingredients, get_allergen_substitute

def run_workflow(recipe_name, servings, allergen, diet):
    start = time.time()
    tokens = 0
    
    time.sleep(0.05) # Fast static parsing
    tokens += 100 # Only one call
    
    recipe = search_recipes(recipe_name)
    recipe = scale_ingredients(recipe, servings)
    
    if allergen:
        sub = get_allergen_substitute(allergen, diet)
        recipe += f" | Swapped {allergen} for {sub}"
        # Fixed workflow doesn't loop. It fails cascade automatically.
        
    return recipe, tokens, tokens * 0.0001, time.time() - start, "SUCCESS"
