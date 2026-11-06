# Decisions

## 2026-11-03 — PostgreSQL for application storage

The owner chose PostgreSQL rather than SQLite. Customers, orders, tickets, reviews,
and proposals are relational data, so one PostgreSQL database fits the documented
architecture without introducing another datastore. Local development uses the
official PostgreSQL 16 image with Compose and a persistent volume, giving contributors
the same major version and startup command. This adds a running database service to
local setup. Port 5433 avoids colliding with a default local PostgreSQL installation.

Use Psycopg directly for the first database work. It provides connections and
transactions without an additional ORM layer. Schema migrations will be introduced
with the first tables; FastAPI and model-provider dependencies will be added when
their first features need them. No vector store is selected yet.

References: [Psycopg usage](https://www.psycopg.org/psycopg3/docs/basic/usage.html)
and [official PostgreSQL image](https://hub.docker.com/_/postgres).

## 2026-11-03 — Separate schema migrations from fictional seed data

Start with the three tables needed for order lookup rather than creating the entire
PRD schema before its behavior exists. Numbered SQL migrations define the schema;
`schema_migrations` records which files have run. A small Psycopg runner applies
pending files in a transaction. This is a local, forward-only runner for one operator,
without concurrent execution or migration-file checksum validation. Use a mature
migration tool before multiple deployers manage shared environments.

Seed data is separate, explicit, transactional, and preserves rows with existing
IDs. This lets developers rerun setup without resetting their work. Missing dates
stay NULL because fictional fixture gaps should not become invented order facts.
Prices use PostgreSQL `numeric(12, 2)` and Python `Decimal` for exact money values.
Foreign keys and checks enforce record relationships, valid statuses and tiers,
nonnegative prices, and positive quantities at the database boundary.

PostgreSQL integration tests use disposable schemas. They exercise the real engine
while leaving development tables intact. `docs/` remains the project reference;
`kb/` will hold the separately retrievable company articles with source IDs.

## 2026-11-03 — Local BGE retrieval over complete short articles

The owner selected `BAAI/bge-small-en-v1.5` to avoid paid embedding API calls.
Sentence Transformers loads a pinned model revision on CPU with remote code disabled.
Document embeddings are normalized; queries use the same model and BGE's recommended
query instruction. The index records the model revision and encoding convention so
search never compares vectors from a different configuration.

The 22 source-ID sections of the knowledge pack are copied into individual `kb/`
files, retaining their policy text and marking internal guidance. Each short article
is one chunk. This avoids splitting tables and detaching exceptions from rules.
The model tokenizer rejects content beyond its actual limit instead of silently
dropping text. Longer future articles will need a token-aware chunker and multiple
chunk IDs per source; no generic splitter is needed for the current corpus.

A new migration enables pgvector and adds `kb_chunks` with 384-dimensional vectors,
passage text, audience, model identity, and a SHA-256 content version. The Compose
image changes to `pgvector/pgvector:pg16`, preserving the PostgreSQL major version
and existing volume. Exact cosine search is sufficient for 22 passages; approximate
indexes and keyword/hybrid ranking are deferred. Similarity is a ranking signal,
not an answerability threshold or calibrated confidence.

Reindexing replaces only derived KB rows atomically after all embeddings succeed.
It removes stale passages and preserves the working index on failure. Historical
index snapshots are not retained; later traces must preserve the evidence used.
Internal results remain available to the support workflow but must not be exposed
directly as customer answers. No chat LLM or generation step is part of this slice.

References: [BGE model card](https://huggingface.co/BAAI/bge-small-en-v1.5),
[Sentence Transformers](https://sbert.net/docs/package_reference/sentence_transformer/model.html),
and [pgvector](https://github.com/pgvector/pgvector).

## 2026-11-03 — Environment-configured embedding model

The owner requested changing models through `.env` rather than Python constants.
Model name and revision are now required environment settings; query and document
prefixes are configurable too, since retrieval models can require different input
instructions. `.env.example` supplies the BGE configuration. The generic `Embedder`
loads these values once per process. Its index identity includes the model, revision,
both prefixes, and normalization convention; any change requires restarting and
rebuilding the index. A dimension check rejects models incompatible with the current
384-dimensional schema before database writes. Dimension changes remain explicit
migrations rather than automatic destructive schema changes.

Automatic KB watching was discussed as a possible next slice, not implemented.
The explicit index command already includes new files and removes deleted ones
when rerun, while preserving the working index if validation or embedding fails.

## 2026-11-03 — First evidence-based policy draft, before ticket automation

The owner requested completing RAG with an answering mechanism and then testing it.
Use the official Google Gen AI SDK and the model already configured in `.env`.
No fallback changes the model or spends against another provider automatically.
The gateway validates structured JSON with Pydantic, bounds requests, exposes usage,
and sanitizes errors without printing keys or provider request details.

The first generation slice handles fictional policy questions only. It excludes
internal passages from evidence and abstains on unavailable or customer-specific
facts. Candidate replies must cite retrieved source IDs with actual quotes, then
pass a separate grounding call. All drafts still require human review; every failure
returns an escalation result without exposing the rejected draft. The same model
acts as generator and checker, so failures can correlate; this is risk reduction,
not proof of correctness. Independent evals and human review remain necessary.

Each question makes at most two calls, without retries, each capped at 2,048 output
tokens and a 30-second request timeout. Durable ticket processing, comprehensive PII
redaction/escalation rules, cost ceilings, and trace persistence are deferred and
must precede use with real inbound tickets. Live smoke tests use four synthetic
questions and distinguish service failures from expected abstention. The user's
mention of “200” was clarified as a typo, not a request for 200 test cases.

References: [Google Gen AI SDK](https://googleapis.github.io/python-genai/)
and [structured outputs](https://aistudio.google.com/docs/structured-output).
