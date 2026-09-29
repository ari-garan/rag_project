# AgentCard: Kitchen Orchestrator

- **Skills:** Recipe retrieval, ingredient scaling, allergen verification, dietary substitutions.
- **Input/Output Modes:** Text-in / Text-out (Markdown).
- **Auth:** Standard Bearer token (JWT), scoped read-only to recipe corpus.

**A2A Task Lifecycle (Failed Case Q2):**
When the Allergen Worker returned a 500, the task lifecycle should have paused at `input-required`. Instead of degrading silently, it should have asked the user for their explicit allergy list to manually bypass the dead worker. 

**What A2A buys over a REST call:**
A plain REST call expects a structured JSON response and fails rigidly; A2A allows the sub-agent to reason about the failure, ask clarifying questions back to the orchestrator, or return a natural language explanation of *why* the task could not be completed.
