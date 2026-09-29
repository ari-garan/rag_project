# Verdict: KILL the Multi-Agent Orchestrator

Despite the hype around multi-agent systems, the evidence requires us to KILL the orchestrator and KEEP the single agent. 

The orchestrator delivered the exact same 80% pass rate as the single agent, but it drove our p99 latency up to 9.8s (vs 3.5s) and bloated our cost per question significantly due to the massive 4.4x context re-send penalty during hand-offs. I acknowledge the sunk-cost bias here—we spent a full week building this complex orchestrator squad, so it hurts to throw it away—but deploying it would just mean paying 4x more for a slower version of the exact same product.
