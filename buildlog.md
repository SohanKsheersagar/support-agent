# Build log

This is the handoff for continuing the project. Read it alongside `AGENTS.md` and the three Trailhaven source documents in `docs/`. Git history records individual edits; this log preserves the context needed to make the next change.

## 2026-11-03 15:59:27 IST (+05:30) — Foundation ready; implementation not started

### Goal and working agreement

Build a support-agent harness for fictional retailer Trailhaven, with tools, bounded workflows, grounded context, guardrails, evals, memory, and human feedback. The owner is learning while building: complete one small, understandable change, explain its purpose, verify it, commit it, and wait for review before continuing.

### Current state

The three source documents have been read. They define the product, company policies, mock data, 32 initial eval scenarios, and build sequence. The repo contains working instructions and the folder structure from that build plan. All code folders contain only `.gitkeep` placeholders.

There is no runnable application, dependency configuration, database, seed data, test suite, or model integration yet. No runtime behavior has been verified. Documentation diffs have passed whitespace checks; that provides no evidence about agent quality or safety.

### Direction established so far

- Follow the spec's fixed pipeline with a bounded tool loop. This makes tool use, failures, and budgets easier to understand and test.
- Keep customer replies behind human review in the MVP. Forced escalation hands a human a summary without drafting a customer reply. The model may propose financial actions; deterministic policy code must control execution.
- Start offline with mock systems and a CLI before building the UI. Python, FastAPI, Pydantic, and a plain Python orchestrator are the documented direction; dependencies and database choice have not yet been implemented.
- Human feedback should improve reviewed examples, KB content, and regression coverage. It must not silently change policy or carry another customer's private data into a reply. The feedback mechanism has not been built.

These are working constraints from the source docs and owner discussion, not implemented guarantees. `docs/decisions.md` has not been created; use it for durable implementation choices and trade-offs as they arise, and link them here.

### Open questions and gaps

Resolve these before implementing the affected behavior:

- E17 expects `review` while also describing escalation when the KB lacks an answer. Reconcile this with the PRD and escalation matrix before encoding its expected route.
- E01 assumes a carrier inquiry is warranted after three business days without movement. Its last scan is Thursday, October 29, and mock today is Monday, November 2. Define business-day counting and reconcile the fixture with the expectation.
- Reviewer authentication and role enforcement, duplicate-action prevention on retries, and invalidation of approval when a proposal changes need explicit behavior before action execution is implemented.
- Decide how examples are checked before reuse and excluded when stale or private. Storing an approved reply alone does not make it suitable memory for another customer.
- The initial eval set has 32 cases; the project requires at least 40 before completion. Add meaningful regression cases from discovered gaps and failures.

### Next small step

Propose a minimal Python setup and one offline mock order lookup for `TH-10482`, with a focused test for the expected backpack and price. Choose and explain the storage approach before implementing it; SQLite is permitted by the spec but has not been selected. Add exact setup and test commands to `AGENTS.md` when executable code exists. Leave the remaining tables, model calls, and UI for later reviewable steps.
