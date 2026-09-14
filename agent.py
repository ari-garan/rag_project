import time
from tools import search_recipes, scale_ingredients, get_allergen_substitute, DietRestriction

MAX_ITERATIONS = 5
MAX_TOKENS = 2000
MAX_COST = 0.10
MAX_TIME = 10.0

def run_agent(recipe_name, servings, allergen, diet, force_budget_fail=False):
    start = time.time()
    tokens = 0
    iterations = 0
    state = "init"
    current_recipe = ""
    current_allergen = allergen
    
    # Intentionally lower budget if we want to log a termination
    budget_time_limit = 0.1 if force_budget_fail else MAX_TIME
    
    while True:
        iterations += 1
        
        # 1. Enforce Budgets
        if iterations > MAX_ITERATIONS:
            return None, tokens, tokens * 0.0001, time.time() - start, "MAX_ITERATIONS_EXCEEDED"
        if tokens > MAX_TOKENS:
            return None, tokens, tokens * 0.0001, time.time() - start, "MAX_TOKENS_EXCEEDED"
        if (tokens * 0.0001) > MAX_COST:
            return None, tokens, tokens * 0.0001, time.time() - start, "MAX_COST_EXCEEDED"
        if time.time() - start > budget_time_limit:
            return None, tokens, tokens * 0.0001, time.time() - start, "MAX_TIME_EXCEEDED"
            
        time.sleep(0.1) # Simulate LLM thinking
        tokens += 200 # Agent passes history every loop
        
        if state == "init":
            current_recipe = search_recipes(recipe_name)
            state = "scale"
        elif state == "scale":
            current_recipe = scale_ingredients(current_recipe, servings)
            if current_allergen:
                state = "swap"
            else:
                state = "done"
        elif state == "swap":
            sub = get_allergen_substitute(current_allergen, DietRestriction(diet))
            if "Warning" in sub:
                current_allergen = sub.split()[0] # cascade
            else:
                current_recipe += f" | Final Swap: {sub}"
                state = "done"
        elif state == "done":
            break
            
    return current_recipe, tokens, tokens * 0.0001, time.time() - start, "SUCCESS"

if __name__ == "__main__":
    # Test run to make the agent runnable by one command
    res, tok, cost, lat, status = run_agent("Thai Curry", 4, "peanuts", "nut_free")
    print(f"Agent Result: {res}\nTokens: {tok}, Cost: ${cost:.4f}, Latency: {lat:.3f}s, Status: {status}")
