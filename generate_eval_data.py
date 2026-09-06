import json

# Generate 25 cases for eval_set.json
cases = []
labels = {}

modes = ["flavour-plausibility", "texture-failure", "measurement-error", "allergen-safety"]

for i in range(1, 24):
    mode = modes[i % len(modes)]
    
    case = {
        "id": f"case_{i}",
        "mode": mode,
        "input_recipe": f"Recipe {i}: standard instructions.",
        "substitution_request": "Substitute ingredient X with Y.",
        "generated_output": f"Use Y instead of X. Proceed with Recipe {i}.",
        "allergen_ingredient": "peanuts" if mode == "allergen-safety" else None,
        "needs_oven_temp": True if mode == "texture-failure" else False
    }
    
    # Make some fail assertions intentionally
    if mode == "allergen-safety" and i % 2 == 0:
        case["generated_output"] += " Warning: contains nuts." # Pass
    
    if mode == "texture-failure" and i % 2 == 0:
        case["generated_output"] += " Bake at 350 F." # Pass
        
    # Simulate a human label
    labels[case["id"]] = 1 if i % 3 != 0 else 0
    cases.append(case)

# Add 2 regression cases
cases.append({
    "id": "case_24_regression",
    "mode": "regression",
    "input_recipe": "Chicken Biryani: 1kg chicken, 2 cups rice, 1 tbsp salt.",
    "substitution_request": "Double the recipe.",
    "generated_output": "2kg chicken, 4 cups rice, 1 tbsp salt.", # Fails measurement (salt not doubled)
    "allergen_ingredient": None,
    "needs_oven_temp": False
})
labels["case_24_regression"] = 0

cases.append({
    "id": "case_25_regression",
    "mode": "regression",
    "input_recipe": "Peanut Sauce: 1 cup peanut butter, soy sauce, lime.",
    "substitution_request": "Make it soy-free.",
    "generated_output": "Use coconut aminos instead of soy sauce. Warning: contains nuts.",
    "allergen_ingredient": "peanut butter",
    "needs_oven_temp": False
})
labels["case_25_regression"] = 1

with open('eval_set.json', 'w') as f:
    json.dump(cases, f, indent=2)

with open('labels_25.json', 'w') as f:
    json.dump(labels, f, indent=2)

print("Generated eval_set.json and labels_25.json")

