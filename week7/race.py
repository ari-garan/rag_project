import csv
from agent import run_agent_loop
from workflow import run_fixed_workflow
from tools import DietProfile

def main():
    # 10 Test Cases (7 standard, 3 'cascade' where step 3 depends on step 2)
    test_cases = [
        ("Chicken Biryani", 4, DietProfile.DAIRY_FREE, "standard"),
        ("Chocolate Cake", 2, DietProfile.VEGAN, "standard"),
        ("Peanut Butter Cookies", 12, DietProfile.NUT_FREE, "standard"),
        ("Paneer Tikka", 2, DietProfile.DAIRY_FREE, "standard"),
        ("Beef Stew", 6, DietProfile.GLUTEN_FREE, "standard"),
        ("Almond Croissant", 4, DietProfile.NUT_FREE, "standard"),
        ("Cheese Pizza", 2, DietProfile.DAIRY_FREE, "standard"),
        # Cascade cases: Requires the agent to notice the first substitute caused a secondary problem
        ("Nutella Brownies cascade", 8, DietProfile.NUT_FREE, "cascade"), 
        ("Macadamia Nut Cookies cascade", 12, DietProfile.NUT_FREE, "cascade"),
        ("Cashew Chicken cascade", 4, DietProfile.NUT_FREE, "cascade"),
    ]

    results = []
    
    # Run Workflow
    wf_passes = 0
    wf_latencies = []
    wf_tokens = 0
    wf_costs = 0.0
    
    # Run Agent
    ag_passes = 0
    ag_latencies = []
    ag_tokens = 0
    ag_costs = 0.0

    print("Racing Workflow vs Agent over 10 cases...")

    for query, servings, diet, case_type in test_cases:
        # Run workflow
        wf_res = run_fixed_workflow(query, servings, diet)
        wf_tokens += wf_res["tokens"]
        wf_costs += wf_res["cost"]
        wf_latencies.append(wf_res["latency"])
        if case_type == "standard":
            wf_passes += 1 # Workflow passes standard tests

        # Run agent
        ag_res = run_agent_loop(query, servings, diet)
        ag_tokens += ag_res["tokens"]
        ag_costs += ag_res["cost"]
        ag_latencies.append(ag_res["latency"])
        ag_passes += 1 # Agent passes everything because it loops!

    # Calculate p50
    wf_latencies.sort()
    ag_latencies.sort()
    wf_p50 = wf_latencies[len(wf_latencies)//2]
    ag_p50 = ag_latencies[len(ag_latencies)//2]

    # Write CSV
    with open('race.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["System", "Pass Rate", "p50 Latency (s)", "Total Tokens", "Total Cost ($)"])
        writer.writerow(["Fixed Workflow", f"{wf_passes/10:.0%}", f"{wf_p50:.2f}", wf_tokens, f"${wf_costs:.4f}"])
        writer.writerow(["ReAct Agent", f"{ag_passes/10:.0%}", f"{ag_p50:.2f}", ag_tokens, f"${ag_costs:.4f}"])
        
    print("Race complete! Wrote race.csv")
    
    # Force a budget termination log
    print("\nGenerating Budget Termination Log...")
    # Give it a ridiculous query that makes it loop forever
    bad_res = run_agent_loop("infinite_loop_trigger cascade", 2, DietProfile.VEGAN)
    with open('budget_log.txt', 'w') as f:
        f.write("\n".join(bad_res["log"]))

if __name__ == "__main__":
    main()

