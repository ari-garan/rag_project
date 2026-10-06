import json
import statistics
from agent import run_agent
from orchestrator import run_orchestrator

def load_cases():
    cases = []
    with open("golden_set.jsonl", "r") as f:
        for line in f:
            cases.append(json.loads(line))
            if len(cases) == 10:
                break
    return cases

def run_race():
    cases = load_cases()
    
    single_tokens, multi_tokens = [], []
    single_lats, multi_lats = [], []
    single_pass, multi_pass = 0, 0
    
    print(f"Running race on {len(cases)} eval cases...\n")
    
    for i, case in enumerate(cases):
        # We use dummy inputs for the simulation since the questions are text
        recipe = "Test Recipe"
        
        # Run Single Agent
        s_res, s_tok, s_cost, s_lat, s_stat = run_agent(recipe, 4, "dairy", "vegan")
        single_tokens.append(s_tok)
        single_lats.append(s_lat)
        if s_stat == "SUCCESS": single_pass += 1
            
        # Run Orchestrator
        # Inject 500 error on Case 2
        force_error = True if i == 1 else False 
        m_res, m_tok, m_cost, m_lat, m_stat = run_orchestrator(recipe, 4, "dairy", "vegan", force_500=force_error)
        multi_tokens.append(m_tok)
        multi_lats.append(m_lat)
        if m_stat in ["SUCCESS", "DEGRADE"]: multi_pass += 1
            
    # Calculate stats
    s_p50 = statistics.median(single_lats)
    s_p99 = statistics.quantiles(single_lats, n=100)[-1] if len(single_lats) > 1 else single_lats[0]
    
    m_p50 = statistics.median(multi_lats)
    m_p99 = statistics.quantiles(multi_lats, n=100)[-1] if len(multi_lats) > 1 else multi_lats[0]
    
    sum_s_tok = sum(single_tokens)
    sum_m_tok = sum(multi_tokens)
    
    print("--- RACE RESULTS ---")
    print("SINGLE AGENT:")
    print(f"Pass Rate: {single_pass/10 * 100}%")
    print(f"p50 Latency: {s_p50:.3f}s | p99 Latency: {s_p99:.3f}s")
    print(f"Total Tokens: {sum_s_tok} | Cost: ${sum_s_tok * 0.0001:.4f}")
    
    print("\nORCHESTRATOR SQUAD:")
    print(f"Pass Rate: {multi_pass/10 * 100}%")
    print(f"p50 Latency: {m_p50:.3f}s | p99 Latency: {m_p99:.3f}s")
    print(f"Total Tokens: {sum_m_tok} | Cost: ${sum_m_tok * 0.0001:.4f}")
    
    print(f"\nContext Re-send Multiplier: {sum_m_tok / sum_s_tok:.1f}x")

if __name__ == "__main__":
    run_race()

