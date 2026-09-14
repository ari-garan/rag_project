import csv
from agent import run_agent
from workflow import run_workflow

requests = [
    # 7 standard requests
    {"name": "Cake", "servings": 2, "allergen": "milk", "diet": "dairy_free", "cascade": False},
    {"name": "Pie", "servings": 4, "allergen": "egg", "diet": "vegan", "cascade": False},
    {"name": "Stew", "servings": 1, "allergen": "beef", "diet": "vegan", "cascade": False},
    {"name": "Salad", "servings": 2, "allergen": "cheese", "diet": "dairy_free", "cascade": False},
    {"name": "Soup", "servings": 4, "allergen": "butter", "diet": "dairy_free", "cascade": False},
    {"name": "Pasta", "servings": 2, "allergen": "cream", "diet": "dairy_free", "cascade": False},
    {"name": "Bread", "servings": 1, "allergen": "milk", "diet": "dairy_free", "cascade": False},
    # 3 cascade requests (peanuts -> almonds -> sunflower seeds)
    {"name": "Thai Curry", "servings": 4, "allergen": "peanuts", "diet": "nut_free", "cascade": True},
    {"name": "Satay", "servings": 2, "allergen": "peanuts", "diet": "nut_free", "cascade": True},
    {"name": "Brownies", "servings": 8, "allergen": "peanuts", "diet": "nut_free", "cascade": True},
]

def run_race():
    agent_metrics = {"pass": 0, "latencies": [], "tokens": 0, "cost": 0.0}
    wf_metrics = {"pass": 0, "latencies": [], "tokens": 0, "cost": 0.0}
    
    for req in requests:
        # Agent
        a_res, a_tok, a_cost, a_lat, a_status = run_agent(req['name'], req['servings'], req['allergen'], req['diet'])
        agent_metrics["latencies"].append(a_lat)
        agent_metrics["tokens"] += a_tok
        agent_metrics["cost"] += a_cost
        if a_status == "SUCCESS" and "Warning" not in a_res:
            agent_metrics["pass"] += 1
            
        # Workflow
        w_res, w_tok, w_cost, w_lat, w_status = run_workflow(req['name'], req['servings'], req['allergen'], req['diet'])
        wf_metrics["latencies"].append(w_lat)
        wf_metrics["tokens"] += w_tok
        wf_metrics["cost"] += w_cost
        if w_status == "SUCCESS" and "Warning" not in w_res:
            wf_metrics["pass"] += 1

    a_latencies = sorted(agent_metrics["latencies"])
    w_latencies = sorted(wf_metrics["latencies"])
    
    data = [
        ["System", "Pass Rate", "p50 Latency (s)", "Total Tokens", "Cost per Task ($)"],
        ["Agent", f"{agent_metrics['pass']}/10", f"{a_latencies[len(a_latencies)//2]:.3f}", f"{agent_metrics['tokens']}", f"{agent_metrics['cost']/10:.4f}"],
        ["Workflow", f"{wf_metrics['pass']}/10", f"{w_latencies[len(w_latencies)//2]:.3f}", f"{wf_metrics['tokens']}", f"{wf_metrics['cost']/10:.4f}"]
    ]
    
    with open('race.csv', 'w', newline='') as f:
        import csv
        writer = csv.writer(f)
        writer.writerows(data)
        
    # Generate budget log
    _, _, _, _, status = run_agent("Test", 1, "peanuts", "nut_free", force_budget_fail=True)
    with open('budget_log.txt', 'w') as f:
        f.write(f"Agent execution terminated cleanly by budget constraint: {status}")

if __name__ == '__main__':
    run_race()
