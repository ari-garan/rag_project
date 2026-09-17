import time
from tools import search_recipe, scale_recipe, substitute_ingredient, DietProfile

# Budgets
MAX_ITERS = 5
MAX_TOKENS = 4000
MAX_COST = 0.05
MAX_TIME_SEC = 10.0

def mock_llm_call(prompt: str, iteration: int, query: str):
    """Simulates an LLM picking the next tool based on the prompt history."""
    if iteration == 1:
        return "Action: search_recipe", 300, 0.001
    elif iteration == 2:
        return "Action: scale_recipe", 450, 0.002
    elif iteration == 3:
        return "Action: substitute_ingredient", 600, 0.003
    elif iteration == 4 and "cascade" in query:
        # Agent realizes the substitute was also an allergen, loops again!
        return "Action: substitute_ingredient", 750, 0.004
    else:
        return "Action: finish", 200, 0.001

def run_agent_loop(query: str, servings: int, diet: DietProfile):
    start_time = time.time()
    total_tokens = 0
    total_cost = 0.0
    iterations = 0
    
    context = ""
    log = []
    
    while True:
        iterations += 1
        
        # 1. Enforce Budgets
        wall_clock = time.time() - start_time
        if iterations > MAX_ITERS:
            log.append(f"[BUDGET TERMINATION] Max iterations ({MAX_ITERS}) reached.")
            break
        if total_tokens > MAX_TOKENS:
            log.append(f"[BUDGET TERMINATION] Max tokens ({MAX_TOKENS}) exceeded.")
            break
        if total_cost > MAX_COST:
            log.append(f"[BUDGET TERMINATION] Max cost (${MAX_COST}) exceeded.")
            break
        if wall_clock > MAX_TIME_SEC:
            log.append(f"[BUDGET TERMINATION] Max wall-clock time ({MAX_TIME_SEC}s) exceeded.")
            break
            
        # 2. LLM Call
        prompt = f"History: {context}\nNext action?"
        action, tokens, cost = mock_llm_call(prompt, iterations, query)
        total_tokens += tokens
        total_cost += cost
        
        # 3. Parse and Execute Action
        if "search_recipe" in action:
            res = search_recipe(query)
            context += f"\nFound: {res}"
        elif "scale_recipe" in action:
            res = scale_recipe(context, servings)
            context = res
        elif "substitute_ingredient" in action:
            res = substitute_ingredient(context, diet)
            context = res
        elif "finish" in action:
            break
            
    latency = time.time() - start_time
    
    return {
        "output": context,
        "latency": latency,
        "tokens": total_tokens,
        "cost": total_cost,
        "system": "Agent",
        "log": log
    }

