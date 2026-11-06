# Build log

This is the handoff for continuing the project. Read it alongside `AGENTS.md` and the three Trailhaven source documents in `docs/`. Git history records individual edits; this log preserves the context needed to make the next change.

## 2026-11-06 12:09:24 IST (+05:30) — Generation slice approved for commit and push

The owner approved committing and pushing the generation slice described below to `main`. Before publishing, the offline suite passed 21 tests, with five opt-in database/model tests skipped; whitespace checks passed. `.env` remains ignored and excluded. The previous live 0/4 report is retained as failure evidence; no new Gemini requests were made. The next useful step remains a successful live RAG run and human inspection of answers, not additional agent features. Commit/push approval does not authorize a new implementation slice.

## 2026-11-03 17:34:13 IST (+05:30) — Earlier checkpoint: draft generation implemented

The owner authorized committing the reviewed RAG/configuration work, now `d7874c4`, and adding an answering mechanism before testing the full RAG flow. “200” was clarified as a typo, not 200 test cases. The new generation slice is uncommitted for review.

### Implemented behavior

`app/gateway/gemini.py` uses the official SDK with `.env` credentials, validated structured JSON, per-request timeout and output-token bounds, and no automatic retries. Provider error details are suppressed; only status codes are surfaced. `app/orchestrator/rag.py` retrieves up to five passages, excludes internal guidance, asks Gemini for a policy-only draft or abstention, validates citation IDs and exact quotes, rejects forbidden promises, and uses a second call to check grounding and citation support. Results are either `human_review` or `escalate_to_human` with no rejected draft. There are no send/action tools or persisted human tickets.

### Evidence and unresolved issue

The 25-test regression run passed with PostgreSQL/BGE enabled, including offline simulated Gemini cases for grounding rejection, unavailable evidence, invented citations, forbidden promises, malformed output, and provider errors. A further offline test verifies that service failures never count as correct abstention in eval reports. The final offline run passed 21 tests and skipped the five opt-in database/model cases; whitespace checks passed.

The four live synthetic cases in `evals/rag_cases.json` ran through retrieval and Gemini. All four failed the live checks: 504 for care, 503 for discounts, and 504 for both unknown snow load and the instruction override. They escalated without drafts. The expected care and discount source IDs were retrieved. Results are saved in `evals/results/rag-20261103T115218132151Z.json`; the 0/4 result is a provider-availability failure, not demonstrated answer quality. A separate SDK metadata request successfully recognized configured `models/gemini-3.8-flash`. No model fallback or `.env` credential/model change was made, and the secret was never inspected or displayed.

### Continue from here

Review the gateway, draft workflow, and tests, then rerun `uv run --env-file .env python -m evals.run_rag` when generation service is available. The runner now exits nonzero on failures. Do not mark RAG answer quality verified until supported drafts and evidence-based abstention actually pass live tests and human inspection. Avoid repetitive retries against an unavailable service.

This remains a developer-only CLI for fictional policy questions: PII redaction, deterministic escalation rules, ticket persistence, full budget accounting, and durable traces are not implemented. Use no real customer data. The grounding checker is another call to the same model, not a correctness guarantee. Await review and explicit commit authorization before the next slice.

## 2026-11-03 17:16:09 IST (+05:30) — Earlier checkpoint: local environment aligned with template

The owner added a Gemini key to `.env` and requested that local runs use it without inspecting the secret. `.env.example` now documents an empty `GEMINI_API_KEY` placeholder and `GEMINI_MODEL=gemini-3.8-flash` alongside the database and embedding settings. Missing embedding settings and `GEMINI_MODEL` were appended to the existing `.env`; all existing values, including the key, were preserved. Only variable names were checked, and no secret values were displayed or inspected. Git confirms `.env` is ignored. Future commands must load `.env`, not use `.env.example` as runtime configuration.

Verification checked that every template variable name exists locally and that the diff has no whitespace errors. Gemini was not called, so API-key validity, account model access, and quota remain unverified. The Gemini gateway is still unimplemented. The owner subsequently authorized committing the reviewed RAG/configuration changes and proceeding to evidence-based draft generation and testing. That next slice must remain uncommitted until reviewed.

## 2026-11-03 17:07:56 IST (+05:30) — Earlier checkpoint: embedding configuration moved to environment

The owner requested model changes without editing Python. `.env.example` now holds `EMBEDDING_MODEL`, `EMBEDDING_REVISION`, and query/document prefixes. Existing private `.env` files were not created or overwritten; copy these entries when configuring a local environment. `Embedder` replaces the BGE-specific class name and reads configuration at initialization. Model identity stored with each vector includes all embedding settings, preventing cross-configuration comparisons. Models must work with Sentence Transformers and produce 384 dimensions; other sizes fail before indexing and require a deliberate schema migration.

The 22-article development index was rebuilt with the new configuration identity. The full suite passed 15 tests using the environment-configured BGE model and PostgreSQL, including new checks for missing configuration, changed revision/prefix identity, configured model loading, query/document prefixes, and incompatible dimensions. Default offline tests passed 10 and skipped 5 database/model checks. README and AGENTS commands now load embedding settings from the env file. See [decisions](docs/decisions.md).

Automatic indexing on KB file changes was discussed but is not implemented or required to run retrieval. The owner can propose that as the next slice; a local watcher could invoke the existing atomic rebuild on additions, edits, and deletions. Current chunking remains one short article per chunk, with oversized input rejected. Both this configuration change and the earlier RAG implementation remain uncommitted pending review.

## 2026-11-03 16:33:21 IST (+05:30) — Earlier checkpoint: BGE/pgvector retrieval working

The owner selected BGE and authorized the KB/retrieval slice. This slice remains uncommitted; no permission to commit it has been given. The previous business-schema slice is committed as `6b90e77`.

### Current retrieval flow

The 22 source-ID sections of the company knowledge pack now live as individual articles in `kb/`. Each has a title and public/internal audience marker. Original policy text is retained; company profile and canned macros without source IDs remain in the reference pack and are not indexed. Project specs and planning docs are excluded from retrieval.

Each current article is one chunk. `app/retrieval/documents.py` loads and validates these files, deriving the source ID from the filename and a content-hash version from the file. `embeddings.py` runs pinned `BAAI/bge-small-en-v1.5` locally on CPU. It rejects text over the model token limit, normalizes embeddings, and adds BGE's retrieval instruction only to questions. An embedding is the resulting vector of 384 numbers; pgvector stores and compares it, not creates it.

Compose now uses the pgvector-enabled PostgreSQL 16 image with the existing data volume. Migration `002_knowledge.sql` enables the extension in `public` and creates `kb_chunks`. The index command computes all vectors before replacing derived KB rows in a transaction. Search returns source ID, title, text, version, audience, and cosine similarity for the top passages, restricted to the pinned embedding configuration. See [decisions](docs/decisions.md) for trade-offs.

### Verification and local state

Dependencies and the pinned model were downloaded; weights are cached outside Git. The database is running and all 22 passages are indexed. The real search CLI returned `KB-CARE-001` first for washing a down sleeping bag.

All 13 tests passed with `TEST_DATABASE_URL` and `RUN_BGE_TESTS=1`, including actual model/pgvector retrieval for care, discount, and shipping queries. Coverage includes rejected oversized input, document version changes, invalid KB/search inputs, vector ranking, model mismatch exclusion, stale-row removal, and preserving the old index when a rebuild fails. PostgreSQL tests use disposable schemas; the shared fixture moved to `tests/conftest.py`. Default offline tests passed 8 and explicitly skipped 5 database/model cases.

### Limits and continuation

This implements retrieval, not generated answers or a working support agent. Internal policies are intentionally available to the future agent; do not expose this CLI's raw results directly to customers. Similarity scores are not calibrated confidence. Search is vector-only: keyword/hybrid ranking, unknown-topic rejection, and wider retrieval evals are still pending. Longer articles will require multiple token-aware chunks; the current approach rejects them safely. Reindexing retains only the active snapshot, so later traces must preserve their cited evidence.

Wait for owner review and the next proposed slice. Possible continuations are improving retrieval coverage, implementing the model gateway and a grounded draft, or returning to identity-safe order lookup. No chat LLM/provider has been selected or integrated.

## 2026-11-03 16:23:02 IST (+05:30) — Earlier checkpoint: schema slice approved

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
