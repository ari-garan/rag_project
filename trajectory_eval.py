import json
import numpy as np

# Define 10 test cases
test_cases = [
    {"id": 1, "recipe": "Cake", "allergen": "milk", "diet": "dairy_free", "expected_outcome": "Cake | Swapped milk for almond_milk (Safe)", "expected_sequences": [["search_recipes", "scale_ingredients", "get_allergen_substitute"], ["scale_ingredients", "search_recipes", "get_allergen_substitute"]]},
    {"id": 2, "recipe": "Cookies", "allergen": "peanuts", "diet": "nut_free", "expected_outcome": "Cookies | Swapped peanuts for sunflower_seeds (Safe)", "expected_sequences": [["search_recipes", "scale_ingredients", "get_allergen_substitute"], ["scale_ingredients", "search_recipes", "get_allergen_substitute"]]},
    {"id": 3, "recipe": "Pie", "allergen": None, "diet": "none", "expected_outcome": "Pie", "expected_sequences": [["search_recipes", "scale_ingredients"], ["scale_ingredients", "search_recipes"]]},
    {"id": 4, "recipe": "Bread", "allergen": "wheat", "diet": "gluten_free", "expected_outcome": "Bread | Swapped wheat for gluten_free_flour", "expected_sequences": [["search_recipes", "scale_ingredients", "get_allergen_substitute"], ["scale_ingredients", "search_recipes", "get_allergen_substitute"]]},
    {"id": 5, "recipe": "Muffins", "allergen": "eggs", "diet": "vegan", "expected_outcome": "Muffins | Swapped eggs for flax_egg", "expected_sequences": [["search_recipes", "scale_ingredients", "get_allergen_substitute"], ["scale_ingredients", "search_recipes", "get_allergen_substitute"]]},
    {"id": 6, "recipe": "Pancakes", "allergen": "milk", "diet": "dairy_free", "expected_outcome": "Pancakes | Swapped milk for oat_milk", "expected_sequences": [["search_recipes", "scale_ingredients", "get_allergen_substitute"], ["scale_ingredients", "search_recipes", "get_allergen_substitute"]]},
    {"id": 7, "recipe": "Waffles", "allergen": None, "diet": "none", "expected_outcome": "Waffles", "expected_sequences": [["search_recipes", "scale_ingredients"], ["scale_ingredients", "search_recipes"]]},
    {"id": 8, "recipe": "Brownies", "allergen": "walnuts", "diet": "nut_free", "expected_outcome": "Brownies | Swapped walnuts for chocolate_chips", "expected_sequences": [["search_recipes", "scale_ingredients", "get_allergen_substitute"], ["scale_ingredients", "search_recipes", "get_allergen_substitute"]]},
    {"id": 9, "recipe": "Pizza", "allergen": "cheese", "diet": "dairy_free", "expected_outcome": "Pizza | Swapped cheese for vegan_cheese", "expected_sequences": [["search_recipes", "scale_ingredients", "get_allergen_substitute"], ["scale_ingredients", "search_recipes", "get_allergen_substitute"]]},
    {"id": 10, "recipe": "Pasta", "allergen": None, "diet": "none", "expected_outcome": "Pasta", "expected_sequences": [["search_recipes", "scale_ingredients"], ["scale_ingredients", "search_recipes"]]}
]

def simulate_agent_run(mitigation_applied=False):
    runs = []
    # Base modes:
    # 1. right_answer_wrong_path: skips get_allergen_substitute but gets outcome right (LLM knowledge)
    # 2. hallucinated_args: calls tool with bad args
    # 3. loop: gets stuck in a loop
    for i, case in enumerate(test_cases):
        run = {"id": case["id"], "cost": 0.0, "steps": 0, "tool_sequence": [], "valid_args": True, "outcome_pass": False, "trajectory_pass": False, "mode": "success"}
        if not mitigation_applied:
            if i == 0 or i == 1: # right answer wrong path (LLM knew the substitute)
                run["tool_sequence"] = ["search_recipes", "scale_ingredients"]
                run["steps"] = 2
                run["cost"] = 0.05
                run["outcome_pass"] = True
                run["trajectory_pass"] = False
                run["mode"] = "right_answer_wrong_path"
            elif i == 2: # hallucinated args
                run["tool_sequence"] = ["search_recipes", "scale_ingredients"]
                run["valid_args"] = False
                run["steps"] = 2
                run["cost"] = 0.05
                run["outcome_pass"] = False
                run["trajectory_pass"] = False
                run["mode"] = "hallucinated_args"
            elif i == 3: # loop
                run["tool_sequence"] = ["search_recipes", "scale_ingredients", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute"]
                run["steps"] = 8
                run["cost"] = 0.25
                run["outcome_pass"] = False
                run["trajectory_pass"] = False
                run["mode"] = "loop"
            else:
                run["tool_sequence"] = ["search_recipes", "scale_ingredients", "get_allergen_substitute"] if case["allergen"] else ["search_recipes", "scale_ingredients"]
                run["steps"] = len(run["tool_sequence"])
                run["cost"] = 0.05
                run["outcome_pass"] = True
                run["trajectory_pass"] = True
                run["mode"] = "success"
        else:
            # MITIGATION: Tighter tool description
            # Fixes right_answer_wrong_path by explicitly forbidding the LLM from answering from its own knowledge
            run["tool_sequence"] = ["search_recipes", "scale_ingredients", "get_allergen_substitute"] if case["allergen"] else ["search_recipes", "scale_ingredients"]
            run["steps"] = len(run["tool_sequence"])
            run["cost"] = 0.06  # Base 0.05 + 0.01 from 100 extra tokens for the tighter prompt
            run["tokens"] = 100 # Extra tokens used
            if i == 2:
                # Hallucinated args still happen (not fixed by this mitigation)
                run["tool_sequence"] = ["search_recipes", "scale_ingredients"]
                run["valid_args"] = False
                run["outcome_pass"] = False
                run["trajectory_pass"] = False
                run["mode"] = "hallucinated_args"
            elif i == 3:
                # Loop still happens (not fixed by this mitigation)
                run["tool_sequence"] = ["search_recipes", "scale_ingredients", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute", "get_allergen_substitute"]
                run["steps"] = 8
                run["cost"] = 0.26
                run["outcome_pass"] = False
                run["trajectory_pass"] = False
                run["mode"] = "loop"
            else:
                run["valid_args"] = True
                run["outcome_pass"] = True
                run["trajectory_pass"] = True
                run["mode"] = "success"
        runs.append(run)
    return runs

def compute_metrics(runs, cases):
    tool_choice_accuracy = sum(1 for r in runs if any(r["tool_sequence"] == seq for seq in [c["expected_sequences"] for c in cases if c["id"] == r["id"]][0])) / len(runs)
    argument_validity = sum(1 for r in runs if r["valid_args"]) / len(runs)
    total_steps_taken = sum(r["steps"] for r in runs)
    total_steps_needed = sum(len([c["expected_sequences"][0] for c in cases if c["id"] == r["id"]][0]) for r in runs)
    step_efficiency = total_steps_taken / total_steps_needed
    costs = [r["cost"] for r in runs]
    cost_p50 = np.percentile(costs, 50)
    cost_max = max(costs)
    outcome_pass_rate = sum(1 for r in runs if r["outcome_pass"]) / len(runs)
    trajectory_pass_rate = sum(1 for r in runs if r["trajectory_pass"]) / len(runs)
    gap = outcome_pass_rate - trajectory_pass_rate
    
    modes = {}
    for r in runs:
        modes[r["mode"]] = modes.get(r["mode"], 0) + 1
        
    return {
        "tool_choice_accuracy": tool_choice_accuracy,
        "argument_validity": argument_validity,
        "step_efficiency": step_efficiency,
        "cost_p50": cost_p50,
        "cost_max": cost_max,
        "outcome_pass_rate": outcome_pass_rate,
        "trajectory_pass_rate": trajectory_pass_rate,
        "gap": gap,
        "modes": modes
    }

print("Running baseline...")
baseline_runs = simulate_agent_run(mitigation_applied=False)
baseline_metrics = compute_metrics(baseline_runs, test_cases)

print("\n--- BASELINE METRICS ---")
print(f"Tool-choice accuracy: {baseline_metrics['tool_choice_accuracy']:.1%}")
print(f"Argument validity: {baseline_metrics['argument_validity']:.1%}")
print(f"Step efficiency: {baseline_metrics['step_efficiency']:.2f}")
print(f"Cost p50: ${baseline_metrics['cost_p50']:.4f}")
print(f"Cost max: ${baseline_metrics['cost_max']:.4f}")
print(f"\nOutcome pass rate: {baseline_metrics['outcome_pass_rate']:.1%}")
print(f"Trajectory pass rate: {baseline_metrics['trajectory_pass_rate']:.1%}")
print(f"Outcome-vs-Trajectory Gap: {baseline_metrics['gap']:.1%}")

right_answer_wrong_path_case = next(r for r in baseline_runs if r["mode"] == "right_answer_wrong_path")
print(f"\nRight-Answer-Wrong-Path Case:")
print(f"ID: {right_answer_wrong_path_case['id']}")
print(f"Trajectory taken: {right_answer_wrong_path_case['tool_sequence']}")
print(f"Expected: {test_cases[right_answer_wrong_path_case['id']-1]['expected_sequences']}")

print("\nApplying mitigation: Tighter tool description")
mitigated_runs = simulate_agent_run(mitigation_applied=True)
mitigated_metrics = compute_metrics(mitigated_runs, test_cases)

print("\n--- MITIGATED METRICS ---")
print(f"Cost p50: ${mitigated_metrics['cost_p50']:.4f}")
print(f"Cost max: ${mitigated_metrics['cost_max']:.4f}")
print(f"Price paid: Added 100 prompt tokens per request, costing +$0.01 per run on average.")

print("\n--- REGRESSION CHECK ---")
all_modes = set(baseline_metrics['modes'].keys()) | set(mitigated_metrics['modes'].keys())
for mode in all_modes:
    b = baseline_metrics['modes'].get(mode, 0)
    a = mitigated_metrics['modes'].get(mode, 0)
    print(f"{mode}: {b} -> {a}")
