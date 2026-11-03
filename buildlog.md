# Build log

This is the handoff for continuing the project. Read it alongside `AGENTS.md` and the three Trailhaven source documents in `docs/`. Git history records individual edits; this log preserves the context needed to make the next change.

## 2026-11-03 16:23:02 IST (+05:30) — Schema slice approved; user directs subsequent steps

The PostgreSQL foundation was committed as `58de11b`. The owner reviewed the schema and seed slice below and explicitly authorized its commit. The ongoing agreement is that the user proposes each next step; validate it, explain corrections, and implement only the agreed small slice. This is recorded in `AGENTS.md`. No further implementation slice is authorized yet.

### Current capability and evidence

The local PostgreSQL container is healthy. `app/db/migrate.py` applied the first numbered SQL migration, creating `customers`, `orders`, and `order_items`, plus a migration ledger. `app/mock/seed.py` loaded the six documented customers, eight orders, and nine items. Seed runs preserve existing rows. Unknown dates remain NULL; Morgan's two prior delivery claims are retained in customer flags. See [decisions](docs/decisions.md) for schema/seed separation and runner limitations.

All six tests passed with `TEST_DATABASE_URL` set, including real PostgreSQL tests in disposable schemas. They verified rerunning migration/seed without duplicates or overwritten edits, the joined `TH-10482` backpack at $179, foreign-key and quantity/price constraints, and rollback of customer inserts when order seeding fails. The actual migration and seed CLIs also completed successfully against the development database. Test schemas were removed by fixture cleanup.

The earlier connectivity-only checkpoint below is historical. Setup, migration, seed, and test commands are in `README.md` and `AGENTS.md`. Unit-only runs skip integration tests unless `TEST_DATABASE_URL` is supplied.

### Boundaries and next step

No customer-facing API or model-accessible order lookup exists yet. Database tests read tables directly; identity verification and authorized tool outputs must be designed before exposing order data to a model. Extra fixtures to reach about 50 orders, remaining PRD tables, and agent behavior are deferred.

`docs/` holds the original project references; `kb/` is the separate location for source-ID-based company articles and is still empty. Populate it in the retrieval slice rather than indexing project planning docs as customer knowledge.

A suggested next slice is the typed, read-only order lookup and its identity boundary; wait for the user's proposal/agreement before implementing it. For retrieval, the intended layout is article files in `kb/` and chunk text, source metadata, and embeddings in PostgreSQL with pgvector. Chunking can be deterministic; an embedding model generates vectors, not pgvector. No embedding model/provider has been selected, pgvector is not installed, and no LLM integration exists. Resolve the existing eval/policy ambiguities when their behavior is implemented. The migration runner is single-operator and forward-only; do not edit an applied SQL file or run concurrent migrations.

## 2026-11-03 16:09:46 IST (+05:30) — Earlier checkpoint: PostgreSQL foundation verified

The owner selected PostgreSQL and reviewed this foundation, then authorized its commit and the next implementation step. Future steps still wait for an explicit instruction before committing; `AGENTS.md` reflects that agreement.

### Working implementation

The project now has Python 3.12 configuration, uv dependency locking, a PostgreSQL 16 Compose service with persistent storage, and `app/db/check.py`, a read-only connectivity check. Only Psycopg and pytest are installed; API and model dependencies are deferred until needed. [Decisions](docs/decisions.md) explains PostgreSQL, local port 5433, and using Psycopg directly.

`README.md` contains setup and verification commands. `.env.example` holds deliberately public local credentials, not production secrets. `.env` is ignored by Git. Verification used the example file explicitly; no private `.env` was created. Docker Desktop was started and the database is running, bound to `127.0.0.1:5433`.

### Evidence and limits

- Compose configuration validated and `docker compose --env-file .env.example up -d --wait db` reported a healthy database.
- `uv run --env-file .env.example python -m app.db.check` returned `PostgreSQL connection OK`, exercising Python-to-PostgreSQL connectivity.
- All three unit tests passed: missing configuration, connection cleanup, and propagation of database failure. These use mocks; the separate smoke check verifies the actual database connection.
- No application tables, mock orders, migrations, API, or agent behavior exist yet. Connection success does not establish any harness safety or eval target.

### Continue from here

The next implementation slice is a versioned schema for customers, orders, and order items, a deterministic mock seed, and a lookup test for `TH-10482`. Use PostgreSQL for integration tests, keep tests isolated from persistent development data, and explain how schema migrations differ from seed data before adding them. The policy and eval questions below remain open.

## 2026-11-03 15:59:27 IST (+05:30) — Earlier checkpoint: implementation not started

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

### Next small step at that checkpoint (superseded above)

Propose a minimal Python setup and one offline mock order lookup for `TH-10482`, with a focused test for the expected backpack and price. Choose and explain the storage approach before implementing it; SQLite is permitted by the spec but has not been selected. Add exact setup and test commands to `AGENTS.md` when executable code exists. Leave the remaining tables, model calls, and UI for later reviewable steps.
