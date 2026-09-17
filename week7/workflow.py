import time
from tools import search_recipe, scale_recipe, substitute_ingredient, DietProfile

def run_fixed_workflow(query: str, servings: int, diet: DietProfile):
    """A hard-coded, sequential workflow. Fast and cheap, but cannot adapt."""
    start_time = time.time()
    tokens_used = 150 # Fixed token cost estimate for workflow
    cost = 0.0001
    
    # Fixed Sequence: Always search -> scale -> substitute
    step1 = search_recipe(query)
    step2 = scale_recipe(step1, servings)
    final_output = substitute_ingredient(step2, diet)
    
    latency = time.time() - start_time
    
    return {
        "output": final_output,
        "latency": latency,
        "tokens": tokens_used,
        "cost": cost,
        "system": "Workflow"
    }

