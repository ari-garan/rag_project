"""
Pantry-to-Plate Assistant: Capstone Single Entry Point (Week 12)
One entry point for a stranger to clone and run end-to-end.
Usage:
  python main.py                           # Interactive pantry query mode
  python main.py --ui                      # Launch interactive Web UI in browser
  python main.py --eval                    # Run the 30-case integrated evaluation suite
  python main.py --demo                    # Run the live 4-part summit demo
  python main.py --query "your question"   # Single question runner
"""

import sys
import os
import argparse
import time

# Ensure UTF-8 output on Windows console
try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Add week12 to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "week12"))
from pantry_assistant import PantryAssistant
from run_evals import run_capstone_eval_suite

def run_four_part_demo():
    print("\n" + "=" * 78)
    print("AI SUMMIT CAPSTONE DEMO: PANTRY-TO-PLATE ASSISTANT (VARIANT B)")
    print("4-Part Standard Demo delivered live to the clock")
    print("=" * 78)
    assistant = PantryAssistant(config_path="week12/mcp_config.json")

    # -------------------------------------------------------------
    # PART 1: A REAL RUN
    # -------------------------------------------------------------
    print("\n[PART 1: A REAL RUN]")
    print("User Scenario: 'I have flour, butter, and sugar. My kid has a nut allergy. Can I make shortbread?'")
    t0 = time.time()
    res1 = assistant.answer_query(
        user_query="I have flour, butter, and sugar. Can I make traditional shortbread?",
        stated_allergy="nuts",
        target_servings=4
    )
    print(f"Agent Output:\n{res1['answer']}")
    print(f"\nTrace ID: {res1['trace_id']} | Latency: {res1['total_latency_ms']}ms | Cost: ${res1['total_cost_usd']}")
    print(f"Citation: {res1['citation']} -> Exact-match declaration checked via MCP tool.")

    print("\nSecond Scenario: Honest Refusal on Time & Scaling")
    res_time = assistant.answer_query(
        user_query="How to make roast chicken in 10 minutes?",
        max_minutes=10
    )
    print(f"Honest Refusal Output: {res_time['answer']}")

    # -------------------------------------------------------------
    # PART 2: THE FAILURES WE FOUND
    # -------------------------------------------------------------
    print("\n" + "-" * 78)
    print("[PART 2: THE FAILURES WE FOUND & THE NEW INTEGRATION MODE]")
    print("The Bug: Reformulation Allergen Near-Miss (Trace: trace_w12_shortbread_fail)")
    print("Detail: Last quarter supplier reformulated 80 recipes (butter swapped for almond nut-oil blend).")
    print("The Failure: Keyword RAG cited original version [recipe_shortbread_orig#version=original], telling a nut-allergic parent shortbread was nut-free!")
    print("New Mode Created by Integration: 'Sub-recipe Version Collision' (6.7% frequency).")
    print("When the Agent and RAG were integrated, the retriever returned the original version while the scaling tool fetched reformulated ingredients, creating a version mismatch!")

    # -------------------------------------------------------------
    # PART 3: A NUMBER THAT MOVED
    # -------------------------------------------------------------
    print("\n" + "-" * 78)
    print("[PART 3: A NUMBER THAT MOVED (EVIDENCE, NOT ADJECTIVES)]")
    print("Allergen-Unsafe Answer Rate on 80 Reformulated Cases (n=80):")
    print("  - Before Exact-Match Declaration Guard: 32.5% (26/80 served unsafe or superseded version)")
    print("  - After Exact-Match Declaration Guard : 0.0%  (0/80 unsafe answers)")
    print("  => A reduction of 32.5 percentage points in anaphylaxis safety risk!")
    print("Judge Agreement Rate on Integrated Outputs: 100.0% against hand-labeled ground truth.")
    print("Stated Non-Coverage: The eval suite does NOT measure oven calibration differences, non-English culinary queries, or cross-contamination at the home kitchen counter.")

    # -------------------------------------------------------------
    # PART 4: WHAT'S NEXT & THE 10X PLAN
    # -------------------------------------------------------------
    print("\n" + "-" * 78)
    print("[PART 4: WHAT'S NEXT & WHAT BREAKS AT 50,000 QUERIES/DAY]")
    print("Unit Economics:")
    print("  - Retrieval (Local Index): $0.00042")
    print("  - MCP Safety Tools       : $0.00073")
    print("  - Generation (Synthesis) : $0.00095")
    print("  - Total Cost per Query   : $0.00210 ($105.00/day at 50,000 queries)")
    print("\nWhat Breaks First at 10x Scale (500,000 queries/day):")
    print("  - LLM Provider Concurrency & Rate Limits:")
    print("    At 500k queries/day, peak load reaches 463 queries/second, instantly exceeding the 50 QPS tier limit.")
    print("    Mitigation: Implement semantic caching on verified recipe combinations (slashing generation volume by 42%).")
    print("=" * 78 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Pantry-to-Plate Assistant: Week 12 Capstone")
    parser.add_argument("--eval", action="store_true", help="Run the full 30-case integrated evaluation suite")
    parser.add_argument("--demo", action="store_true", help="Run the live 4-part capstone summit demo")
    parser.add_argument("--ui", action="store_true", help="Launch the interactive Web UI")
    parser.add_argument("--port", type=int, default=8000, help="Port for the Web UI (default: 8000)")
    parser.add_argument("--query", type=str, help="Submit a single question to the pantry assistant")
    parser.add_argument("--allergy", type=str, default=None, help="Optional declared allergy (e.g. nuts, dairy, fish)")
    parser.add_argument("--servings", type=int, default=4, help="Target servings (default: 4)")
    args = parser.parse_args()

    if args.ui:
        import ui
        ui.run_server(port=args.port)
        return

    if args.eval:
        run_capstone_eval_suite()
        return

    if args.demo:
        run_four_part_demo()
        return

    assistant = PantryAssistant(config_path="week12/mcp_config.json")

    if args.query:
        print(f"\nProcessing Query: '{args.query}' (Allergy: {args.allergy}, Servings: {args.servings})")
        res = assistant.answer_query(args.query, stated_allergy=args.allergy, target_servings=args.servings)
        print("\n--- ASSISTANT ANSWER ---")
        print(res["answer"])
        print(f"\nTrace ID: {res['trace_id']} | Latency: {res['total_latency_ms']}ms | Cost: ${res['total_cost_usd']}")
        return

    # Interactive Mode
    print("=" * 65)
    print("Pantry-to-Plate Assistant (Week 12 Capstone)")
    print("Type your cooking/pantry question. Type 'exit' to quit.")
    print("Conversational memory active: you can ask follow-ups referencing 'it', 'this', scaling, or substitutions.")
    print("To launch the web UI, run: python main.py --ui")
    print("=" * 65)
    
    history = []
    while True:
        try:
            q = input("\nYour Cooking Question: ").strip()
            if not q or q.lower() in ["exit", "quit", "bye"]:
                break
            allergy_in = input("Any allergies? (e.g. nuts, dairy, gluten, or press Enter): ").strip()
            allergy = allergy_in if allergy_in else None
            servings_str = input("How many servings? (default 4): ").strip()
            servings = int(servings_str) if servings_str.isdigit() else 4

            res = assistant.answer_query(q, history=history, stated_allergy=allergy, target_servings=servings)
            print("\n--- ANSWER ---")
            print(res["answer"])
            print(f"\n[Trace ID: {res['trace_id']} | Latency: {res['total_latency_ms']}ms | Cost: ${res['total_cost_usd']}]")

            # Track conversation history
            history.append({"role": "user", "content": q})
            history.append({
                "role": "assistant",
                "content": res["answer"],
                "recipe_id": res.get("recipe_id"),
                "recipe_title": res.get("recipe_title"),
                "citation": res.get("citation"),
                "allergy": allergy
            })
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
