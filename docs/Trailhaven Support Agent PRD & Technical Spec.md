# Trailhaven Support Agent: PRD & Technical Spec

*Doc 1 of 3. Companion docs: Company Knowledge Pack (Doc 2) and Evals, Mock Data & Build Plan (Doc 3).*

Trailhaven is a fictional company created so you have realistic constraints to build against. Treat this document as the source of truth: if the code and this spec disagree, one of them is wrong.

## 1. Overview

**Product:** an AI customer support agent that reads incoming tickets, understands intent, looks up customer and order data, searches the knowledge base, and then either drafts a reply for a human to approve, sends a reply automatically (only for safe, high-confidence cases), or escalates to a human with a clear summary.

**Company:** Trailhaven Outfitters, a direct-to-consumer online store for outdoor gear (tents, backpacks, boots, apparel). About 1,200 support tickets per week across email and web chat. Support team of 9 agents plus 1 team lead. Average first response time today is 9 hours; the target is under 1 hour.

**Problem:** about 60% of tickets are repetitive (where is my order, how do I return this, is this in stock, how do I care for this). Humans spend most of their day on these, and slow replies hurt reviews and repeat purchases.

**Core idea:** the agent handles the repetitive 60% with a human in the loop, and routes the hard 40% to people faster and with better context.

## 2. Goals and non-goals

### Goals

1. Cut median first response time from 9 hours to under 1 hour.
2. Fully resolve or accurately draft replies for at least 60% of tickets.
3. Never take a financially or legally risky action without human approval.
4. Make every agent decision auditable: what it saw, what it did, why.
5. Improve over time from human edits (feedback loop).

### Non-goals (MVP)

- No voice or phone support.
- No multi-language support (English only).
- No proactive outreach (the agent only responds to inbound tickets).
- No real integration with a live Shopify/Zendesk account. MVP uses a mock ticket system and mock order database that mimic their APIs.
- No fine-tuning of models.

## 3. Users

| Persona | Needs | How they use it |
| --- | --- | --- |
| **Support agent (Priya)** | Faster replies, less copy-paste, trust in drafts | Reviews drafts in a queue, edits or approves, sees why the agent suggested it |
| **Team lead (Marcus)** | Control over risk, quality visibility | Approves high-value refunds, monitors quality and cost dashboard, reviews escalations |
| **Customer (Alex)** | Quick, correct, polite answers | Never sees the agent directly; gets replies by email or chat |
| **Admin/developer (you)** | Debuggability | Reads traces, runs evals, tunes prompts and thresholds |

## 4. Scope

### MVP (build this first)

- Ticket ingestion via API endpoint or simple web form that simulates email.
- Classification and priority.
- Knowledge base retrieval (RAG) over the docs in Doc 2.
- Tools: order lookup, customer lookup, KB search, refund proposal, ticket update, escalation.
- Draft reply with citations to KB articles.
- Review queue UI: approve, edit, reject, escalate.
- Guardrails: PII redaction, refund thresholds, tone and policy checks, step and cost budgets.
- Trace logging and a basic metrics page.
- Eval harness with 40+ cases.

### V2 (only if MVP is solid)

- Auto-send for narrow, high-confidence categories.
- Learning from edits via retrieved few-shot examples.
- Chat channel with streaming replies.
- Sub-agent split (triage agent and resolution agent).
- Sentiment-based escalation.

## 5. Functional requirements

Priority: **P0** = must have for MVP, **P1** = should have, **P2** = later.

### Ingestion and triage

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-1 | Accept a ticket (customer email, subject, body, optional order number, channel) via `POST /tickets` | P0 |
| FR-2 | Classify each ticket into one primary category: `order_status`, `returns_refunds`, `shipping_issue`, `product_question`, `warranty_defect`, `account_billing`, `complaint`, `other` | P0 |
| FR-3 | Assign priority (`low`, `normal`, `high`, `urgent`) using rules plus model judgment (e.g. safety issue, legal threat, or repeat contact within 7 days raises priority) | P0 |
| FR-4 | Detect and flag tickets that must always go to a human (see escalation matrix in Doc 2) | P0 |
| FR-5 | Extract entities: order number, product name or SKU, dates, requested action | P0 |

### Resolution

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-6 | Look up the customer and their orders by email or order number | P0 |
| FR-7 | Search the knowledge base and return the top passages with source ids | P0 |
| FR-8 | Draft a reply that follows the tone guide, answers every question in the ticket, and cites KB sources | P0 |
| FR-9 | Propose actions (refund, replacement, return label) as structured proposals, never as free text commitments | P0 |
| FR-10 | Execute a refund only if it passes the refund policy gate (Section 8) | P0 |
| FR-11 | Produce a confidence score and reasons for it | P0 |
| FR-12 | Ask a clarifying question when required information is missing, rather than guessing | P1 |

### Review and routing

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-13 | Route each ticket to one of: `auto_send` (disabled in MVP), `human_review`, `escalate_to_human`, `needs_approval` | P0 |
| FR-14 | Review UI shows ticket, customer and order context, draft, citations, proposed actions, confidence, and a trace link | P0 |
| FR-15 | Humans can approve, edit then approve, reject with a reason, or escalate | P0 |
| FR-16 | Store the original draft, the final sent reply, and the diff | P0 |

### Observability and learning

| ID | Requirement | Priority |
| --- | --- | --- |
| FR-17 | Log a full trace for each ticket (every model call, tool call, input, output, latency, tokens, cost) | P0 |
| FR-18 | Metrics page: volume by category, approval rate, edit rate, escalation rate, average cost per ticket, latency | P1 |
| FR-19 | Retrieve similar past tickets with human-approved replies as examples for new drafts | P1 |
| FR-20 | Nightly eval run that reports pass rate per category | P1 |

## 6. Agent workflow

The workflow is a **fixed pipeline with a bounded loop in the middle**, not a free-roaming agent. This is deliberate: support is high stakes, so predictability beats autonomy.

```
Ticket in
   |
   v
[1] Pre-process: PII redaction for the model, language check, spam check
   |
   v
[2] Classify + prioritize + extract entities  (small/fast model, structured output)
   |
   v
[3] Hard-rule check: does the escalation matrix force a human?  --yes--> [7] Escalate with summary
   |no
   v
[4] Resolution loop (max 6 steps):
      model decides next tool call -> tool runs -> result returned
      tools: lookup_customer, lookup_order, search_kb, check_refund_eligibility, propose_action
   |
   v
[5] Draft reply (larger model) using tone guide + KB passages + order facts + similar approved examples
   |
   v
[6] Self-check + policy gate:
      - every factual claim grounded in a tool result or KB passage?
      - no promises outside policy?
      - no PII leaked, tone correct?
      - confidence >= threshold?
   |pass                      |fail (one retry with feedback, then escalate)
   v                          v
Route: human_review      Escalate with summary
 or needs_approval
   |
   v
[8] Human acts -> store edits -> feedback loop
```

**Loop limits:** max 6 tool calls per ticket, max 2 drafting attempts, max 90 seconds wall time, max $0.10 cost per ticket. Exceeding any limit sends the ticket to a human with whatever was gathered.

## 7. Architecture

### Components

| Component | Responsibility | Suggested tech |
| --- | --- | --- |
| **API service** | Receives tickets, exposes review queue and metrics endpoints | Python + FastAPI |
| **Orchestrator** | Runs the workflow state machine, owns budgets and retries | Plain Python (or LangGraph if you prefer a graph library) |
| **Model gateway** | One module that wraps all LLM calls: retries, timeouts, token and cost accounting, structured output validation | Claude API via the Anthropic SDK; keep the provider swappable |
| **Tool layer** | Typed functions with schemas, permission checks, and input validation | Pydantic models |
| **Knowledge base** | Chunked docs, embeddings, hybrid search (keyword + vector) | Postgres with pgvector (or SQLite + a local vector store for MVP) |
| **Mock business systems** | Fake Shopify (orders, customers) and fake Zendesk (tickets) with realistic data | SQLite or Postgres tables behind small API routes |
| **Guardrail layer** | PII redaction, policy gate, refund gate, output checks | Python module, deterministic code first, model checks second |
| **Memory/feedback store** | Past tickets, final replies, edits, labels | Postgres tables |
| **Trace store** | Every step of every run | Postgres table, or Langfuse/OpenTelemetry if you want a ready-made UI |
| **Review UI** | Queue, ticket detail, approve/edit/reject | React (or Streamlit for fastest MVP) |
| **Eval runner** | Runs test cases through the pipeline, scores results | Python script plus pytest, results saved as JSON |

### How the pieces connect

```
Review UI  <-->  API service  <-->  Orchestrator  <-->  Model gateway  -->  LLM provider
                     |                  |
                     |                  +--> Tool layer --> Mock Shopify / Mock Zendesk / KB search
                     |                  |
                     |                  +--> Guardrail layer
                     |
                     +--> Postgres (tickets, drafts, edits, traces, KB chunks, embeddings)
```

### Key design decisions (write your own reasoning for each in the README)

1. **Fixed pipeline vs fully autonomous loop.** We chose a fixed pipeline with a bounded tool loop for predictability and testability.
2. **Deterministic guardrails first.** Refund limits, PII rules, and escalation triggers are code, not prompts. Prompts can be talked around; code cannot.
3. **Two model sizes.** A small fast model for classification and checks, a stronger model for drafting. This cuts cost and latency.
4. **Structured outputs everywhere.** Classification, proposals, and confidence are validated JSON, not free text.
5. **Human in the loop by default.** Auto-send ships disabled and is switched on per category only after eval results justify it.
6. **Provider-agnostic gateway.** All LLM calls go through one interface so you can compare models in your evals.

## 8. Tools specification

Every tool has a typed input schema, a typed output schema, a permission level, and is logged in the trace.

| Tool | Input | Output | Permission |
| --- | --- | --- | --- |
| `lookup_customer` | `email` | customer id, name, tier, order count, lifetime value, open tickets | read |
| `lookup_order` | `order_id` or `email` | items, prices, dates, status, tracking number, carrier status | read |
| `search_kb` | `query`, `top_k` | passages with `source_id`, title, text, score | read |
| `check_refund_eligibility` | `order_id`, `item_id`, `reason` | eligible (bool), max amount, window days remaining, rule ids applied | read (pure policy calculation) |
| `propose_action` | action type (`refund`, `replacement`, `return_label`, `store_credit`), order, item, amount, reason | proposal id, required approval level | write (creates a proposal only) |
| `execute_refund` | proposal id | success, refund id | write, **callable only by the policy gate**, never directly by the model |
| `update_ticket` | ticket id, category, priority, tags, status | updated ticket | write |
| `escalate_ticket` | ticket id, reason code, summary | escalation record | write |

**Design rule:** the model can *propose* but only deterministic code can *execute* money-moving actions.

## 9. Guardrails

| Guardrail | Implementation |
| --- | --- |
| **PII redaction** | Before model calls, replace card numbers, full addresses, phone numbers with tokens (`[CARD_1]`). Re-insert only in the human-visible UI when needed. Never log raw card data. |
| **Refund approval levels** | Up to $50 and policy-clear: may be pre-approved for execution after human review in MVP. $50.01 to $200: Tier-1 agent approval required. Above $200 or any exception to policy: Team Lead approval required. Details in Doc 2. |
| **Forced escalation** | Safety injury, legal threats, chargebacks, harassment, press or influencer mentions, suspected fraud, accounts flagged VIP. Detected by rules plus classifier; either triggers escalation. |
| **Grounding check** | Second model call verifies each claim in the draft against tool outputs and KB passages. Unsupported claims fail the check. |
| **Prompt injection defense** | Ticket text is treated as untrusted data and wrapped in delimiters; tools never take instructions from ticket content; the model cannot call `execute_refund`. |
| **Tone and policy check** | Banned phrases (e.g. "I guarantee", "we are legally"), required elements (greeting, next step). |
| **Budgets** | Step, time, token, and cost ceilings per ticket and a daily spending cap. |
| **Rate limiting** | Per-IP and per-API-key limits on `POST /tickets` if you host a public demo. |
| **Audit trail** | Immutable trace per ticket. |

## 10. Memory

| Type | Contents | Where |
| --- | --- | --- |
| **Within a ticket (working memory)** | Tool results, extracted entities, draft attempts, check feedback | Orchestrator state, saved to trace |
| **Per customer** | Past tickets, past resolutions, open issues, preferences (e.g. prefers email), flags | `customers` and `tickets` tables, summarized to a short "customer history" block when long |
| **Organizational (long-term)** | KB articles, policies, tone guide, macros | KB store, versioned |
| **Learned examples** | Approved replies and human edits, tagged by category | `reply_examples` table, retrieved by similarity |

Context management rule: the draft prompt gets, in order, the tone guide (short), the ticket, customer summary, order facts, top 3 to 5 KB passages, and up to 2 similar approved examples. Nothing else.

## 11. Feedback loop

1. Human approves, edits, or rejects a draft.
2. System stores `original_draft`, `final_reply`, `edit_distance`, `reject_reason`, and an optional label.
3. Approved or lightly edited replies become candidate few-shot examples. Heavily edited ones go to a weekly review list for you to inspect and turn into new eval cases or KB fixes.
4. Every rejected or escalated ticket the agent should have handled becomes an eval case.
5. Track the **edit rate** and **approval-without-edit rate** over time as the headline quality metrics.

## 12. Data model (core tables)

- `customers(id, email, name, tier, created_at, flags)`
- `orders(id, customer_id, status, placed_at, shipped_at, delivered_at, carrier, tracking_number, total)`
- `order_items(id, order_id, sku, name, price, qty, category)`
- `tickets(id, customer_id, channel, subject, body, category, priority, status, route, created_at)`
- `drafts(id, ticket_id, version, body, citations, confidence, created_at)`
- `proposals(id, ticket_id, type, order_id, item_id, amount, reason, approval_level, status)`
- `reviews(id, draft_id, reviewer, decision, final_body, edit_distance, reason, created_at)`
- `traces(id, ticket_id, step, kind, input, output, latency_ms, tokens_in, tokens_out, cost_usd, created_at)`
- `kb_chunks(id, source_id, title, text, embedding, version)`
- `reply_examples(id, category, ticket_text, final_reply, embedding)`
- `eval_cases(id, input, expected_category, expected_route, expected_facts, must_not_contain)` and `eval_runs(id, case_id, passed, details, run_at)`

## 13. API surface

| Endpoint | Purpose |
| --- | --- |
| `POST /tickets` | Submit a ticket; returns ticket id and starts processing |
| `GET /tickets?status=&route=` | Review queue |
| `GET /tickets/{id}` | Ticket with draft, proposals, context |
| `POST /tickets/{id}/review` | Approve, edit, reject, escalate |
| `POST /proposals/{id}/approve` | Approve a refund or action at the right level |
| `GET /tickets/{id}/trace` | Full trace |
| `GET /metrics` | Dashboard data |
| `POST /kb/reindex` | Rebuild KB index |
| `POST /evals/run` | Run eval suite |

## 14. Non-functional requirements

| Area | Target |
| --- | --- |
| Latency | Draft ready in under 30 seconds at p95 |
| Cost | Under $0.05 average per ticket, hard cap $0.10 |
| Reliability | A model or tool failure never loses a ticket; it falls back to human queue |
| Security | Secrets in environment variables, never in frontend; least-privilege tool permissions; sandboxed mock systems |
| Privacy | Redact PII before model calls; retention limit of 90 days for raw ticket text in the demo |
| Testability | Pipeline runs fully offline against recorded model responses for unit tests |

## 15. Success metrics

| Metric | MVP target |
| --- | --- |
| Classification accuracy on eval set | 90% or higher |
| Correct routing (escalate when required) | 100% on forced-escalation cases, no exceptions |
| Groundedness (no unsupported claims) | 95% or higher |
| Draft approved with no or light edits | 60% or higher on eval set |
| Policy violations in drafts | 0 |
| Average cost per ticket | under $0.05 |

## 16. Milestones

| Phase | Outcome | Rough time |
| --- | --- | --- |
| 0 | Repo, mock data, KB loaded, tracing skeleton | 2 to 3 days |
| 1 | Classification + KB retrieval + draft, CLI only | 3 to 4 days |
| 2 | Tools, bounded loop, refund gate | 4 to 5 days |
| 3 | Guardrails, self-check, escalation matrix | 3 to 4 days |
| 4 | Review UI, feedback storage, metrics | 4 to 5 days |
| 5 | Eval suite, iteration to hit targets | 3 to 5 days |
| 6 | Hosting, rate limits, README, demo video | 2 to 3 days |

## 17. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Model invents policy | Grounding check; cite sources; refuse when KB has no answer and escalate |
| Prompt injection via ticket text | Untrusted-data wrapping; no model access to money-moving tools |
| Wrong refund | Deterministic gate plus human approval above threshold |
| Costs spike on public demo | Daily cap, rate limit, bring-your-own-key option |
| Eval set too easy | Include adversarial and ambiguous cases; add every real failure as a case |
| Over-engineering | Finish phases 1 to 2 as a working CLI before building any UI |

## 18. Definition of done

- All P0 requirements implemented and covered by at least one test or eval.
- Eval targets in Section 15 met and the results file committed.
- README with architecture diagram, design decisions, and trade-offs in your own words.
- Public repo plus hosted demo with rate limiting, plus a 2-minute video.
- You can explain every module without looking at the code.
