# One-Page Architecture Sketch: Pantry-to-Plate Assistant

```mermaid
flowchart TD
    User([User Question + Declared Allergies]) --> InboundGateway[Single Entry Point: main.py / pantry_assistant.py]
    
    subgraph Host["Host Application (Where the Single trace_id & LLM Live)"]
        InboundGateway --> TraceInit["Initialize Trace: trace_id = trace_w12_xxxx\nPII Anonymization (SHA-256 Health Hash)"]
        TraceInit --> Planner["Agent Orchestrator Loop\n(State Machine / Budget Guard)"]
        
        Planner -->|MCP stdio JSON-RPC| ClientSession["MCP Client Session\n(Runtime Tool Discovery via mcp_config.json)"]
        
        subgraph MCPServer["MCP Recipe & Safety Server (Zero Model Calls)"]
            ClientSession --> Tool1["search_recipe_library\n(600-Recipe Catalog & 80 Reformulated Pairs)"]
            ClientSession --> Tool2["check_allergen_field\n(EXACT-MATCH on Structured Fields)"]
            ClientSession --> Tool3["scale_recipe_batch\n(Linear Quantities, Cook Time Constant)"]
            ClientSession --> Tool4["get_safe_internal_temperature\n(Poultry 74°C / 165°F Standards)"]
            ClientSession --> Tool5["get_kitchen_substitution\n(Test-Kitchen Verified Swaps)"]
        end
        
        Tool1 -->|Results + Version Tag| Planner
        Tool2 -->|Status: SAFE / UNSAFE| Planner
        Tool3 -->|Scaled Batch| Planner
        Tool4 -->|Safety Temp| Planner
        Tool5 -->|Swap Data| Planner
        
        Planner --> AssertionGate{"Deterministic Assertion Engine\n(Safety Refusals Executed Here)"}
        AssertionGate -->|Unsafe Allergen / Unsafe Swap| RefusalOut["Instant Safety Refusal\n(Zero Token Waste)"]
        AssertionGate -->|Safe to Synthesize| LLMHostCall["Host Model Call: Synthesis Generation\n(Qwen2.5-72B-Instruct / Local Fallback)"]
    end
    
    LLMHostCall --> PerRequestLog["Per-Request Structured Logging\n(trace_id intact, latency/cost per span -> capstone_traces.jsonl)"]
    RefusalOut --> PerRequestLog
    PerRequestLog --> FinalResponse([User Answer with Mandatory Version Citation\n[recipe_id#version=reformulated-2025]])
```

---

## Where the Model Calls Happen
- **The LLM runs ONLY on the Host side** during the final answer synthesis step (Span 6).
- **The MCP Server contains ZERO model calls.** All MCP server capabilities are deterministic, programmatic, and legal exact-match assertions over structured database fields.
- If an allergen hazard or time impossibility is detected by the MCP tools, the host **short-circuits immediately** with an honest safety refusal, avoiding the LLM generation call entirely.

---

## Where the Money Goes (Cost by Stage)

| Pipeline Stage / Span | Component | Latency (p50) | Tokens | Cost per Request | % of Total Bill |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Span 1: RAG Retrieval** | `search_recipe_library` | 1.8 ms | 420 in | $0.00042 | 20.0% |
| **Span 2: Allergen Check** | `check_allergen_field` | 0.4 ms | 180 in | $0.00018 | 8.6% |
| **Span 3: Recipe Scaling** | `scale_recipe_batch` | 0.3 ms | 210 in | $0.00021 | 10.0% |
| **Span 4: Temperature Check**| `get_safe_internal_temp` | 0.2 ms | 120 in | $0.00012 | 5.7% |
| **Span 5: Substitution Check**| `get_kitchen_substitution` | 0.3 ms | 160 in | $0.00016 | 7.6% |
| **Span 6: Generation** | Host Model Call (Synthesis)| 340.0 ms | 650 out | $0.00095 | 45.2% |
| **Span 7: Per-Request Log** | Disk Write + PII Hash | 0.1 ms | 0 | $0.00006 | 2.9% |
| **TOTAL PER QUERY** | **End-to-End Request** | **~343 ms** | **1,740** | **$0.00210** | **100.0%** |

*Financial Insight:* Generation represents 45.2% of total cost, while local retrieval and MCP safety tools represent the rest. Implementing semantic caching drops repetitive generation queries to $0.00, reducing daily operating cost at 50,000 queries/day from $105.00 to $60.90.
