# Thursday Fresh-Eyes Review Note

**Review Date:** Thursday, Week 12 (Pre-Summit Review)  
**External Reviewer:** Jordan Chen (Squad C — HR Policy Desk)  
**Target Repository:** `rag_project` (Branch: `master`)  
**Assignment:** Clone the repository fresh, execute the system with zero verbal guidance, and evaluate live MCP tool interop.

---

## 1. Where the Reviewer Stumbled

1. **Initial Confusion on Entry Point:**
   - *Stumble:* Jordan opened `app.py` directly (which was our Week 3 legacy RAG file) rather than `main.py`. Because `app.py` had leftover Torch/SentenceTransformer dependencies, it failed to execute on Jordan's Windows laptop with an Application Control DLL block.
   - *Time Lost:* 4 minutes 15 seconds.

2. **Unclear Single-Command Flag:**
   - *Stumble:* Jordan attempted to run `python main.py` and expected an automated evaluation suite to pop up, but the assistant entered interactive input mode and waited for user keyboard input.
   - *Time Lost:* 1 minute 30 seconds.

3. **External MCP Tool Call Schema Assumption:**
   - *Stumble:* When Jordan's Squad C client agent attempted to call our `check_allergen_field` tool over stdio MCP, they passed `{"allergy": "peanuts"}` instead of `{"allergen": "peanuts"}`. Because our schema was strictly typed, it returned an argument validation error without a helpful hint.

---

## 2. What We Changed in Response (Before Friday Demo)

1. **Unified Root `main.py` Entry Point with CLI Flags:**
   - Updated `main.py` with explicit argparse commands:
     - `python main.py --eval` for the full 30-case evaluation suite.
     - `python main.py --demo` for the 4-part live summit demo.
     - `python main.py` for interactive mode.
   - Updated the top-level `README.md` with bold, copy-pasteable commands so a stranger starts correctly on the first attempt.

2. **Forgiving Argument Aliasing on MCP Safety Tools:**
   - Added parameter normalization in `check_allergen_field`: accepts both `allergen` and `allergy` interchangeably, preventing schema collisions from third-party client squads.

3. **Self-Contained Dependency Decoupling:**
   - Decoupled `week12/` completely from system-level DLL dependencies, ensuring 100% pure Python execution across Windows, macOS, and Linux without native binary blocks.
