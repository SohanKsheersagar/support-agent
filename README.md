# Trailhaven support agent

A learning project building a customer-support agent for a fictional outdoor retailer.
The MVP will draft replies for human review and escalate risky cases. It currently
contains PostgreSQL business data and local KB retrieval using BGE and pgvector.
It retrieves passages; it does not generate or send replies yet.

## Local setup

Install Python 3.12, [uv](https://docs.astral.sh/uv/), and Docker with Compose.
Start Docker Desktop (or your Docker engine) before running these commands:
Copy the example only on first setup; preserve an existing `.env` and add missing
settings from the template instead.

```sh
cp .env.example .env
uv sync --locked
docker compose up -d --wait db
uv run --env-file .env python -m app.db.check
uv run --env-file .env python -m app.db.migrate
uv run --env-file .env python -m app.mock.seed
uv run pytest
```

The connection check should print `PostgreSQL connection OK`. Unit tests need no
database, API keys, or network after dependencies have been installed.

Compose reads `.env`; Python receives it explicitly through `uv run --env-file`.
If you change the local password, update both values in `.env`. The sample credentials
are only for this local database, which binds to localhost on port 5433 to avoid
the usual PostgreSQL port. Do not use them for a hosted environment.

Keep real credentials in `.env`, which Git ignores. `.env.example` contains only
sample values and empty secret placeholders. `GEMINI_API_KEY` and `GEMINI_MODEL`
are reserved for the upcoming generation integration; adding them does not make
the current retrieval CLI call Gemini.

```sh
docker compose stop db
```

Stopping preserves data in the named volume. PostgreSQL initialization credentials
apply when that volume is first created; editing `.env` does not change an existing
database password.

## Tables and seed data

`app/db/migrations/001_orders.sql` defines customers, orders, and order items.
The migration command records applied filenames in `schema_migrations` and skips
them on subsequent runs. Run migrations from one process at a time. Once a migration
has been applied, add a new numbered file for changes instead of editing the old one.
Pending migrations and their records are applied in one transaction: a failure rolls
back that run.

`app/mock/seed.sql` contains six customers, eight orders, and nine order items from
the mock-data document. The seed command runs in a transaction and skips existing
IDs without overwriting edits. It is for the fictional development database only.
Unknown dates remain NULL. The extra orders needed to reach about 50 fixtures will
be added later; repeatable policy scenarios use the fixed date `2026-11-02`.

To run integration tests, set `TEST_DATABASE_URL` to a local PostgreSQL database
where the test user can create schemas. For the sample local credentials:

```sh
TEST_DATABASE_URL=postgresql://trailhaven:trailhaven_local@127.0.0.1:5433/trailhaven uv run pytest
```

Each integration test creates a uniquely named schema and removes it afterward;
it never seeds or drops the development tables. Without `TEST_DATABASE_URL`, these
tests are explicitly skipped and only the unit tests run.

## Document locations

`docs/` holds project specifications and design decisions. The original company
knowledge pack stays there as a reference. `kb/` contains its 22 source-ID sections
as policies, FAQs, and tone articles. Filenames are source IDs; each file starts
with a title and `Audience: public` or `Audience: internal`. Only this directory is
indexed, so project specs and build notes cannot become policy search results.

## KB retrieval

The database image includes pgvector while keeping PostgreSQL major version 16 and
the existing data volume. Run `docker compose up -d --wait db` after pulling these
changes, then run migrations to enable the extension and create `kb_chunks`.
The local database user can create extensions; hosted PostgreSQL may require an
administrator to enable `vector` in the `public` schema first.

```sh
uv run --env-file .env python -m app.retrieval.index
uv run --env-file .env python -m app.retrieval.search "How do I wash my down sleeping bag?"
```

The first command downloads the model configured in `.env` on first use,
runs it locally on CPU, and stores 384-number normalized embeddings. No API key or
paid inference service is needed. Model weights live in the Hugging Face cache,
not Git. Dependencies and weights require disk space and internet on first setup.

Each current article is one chunk so complete policy rules stay together. The
encoder checks token lengths and rejects oversized articles/queries instead of
silently truncating them. Documents are embedded with their titles; queries use
BGE's recommended retrieval prefix from `.env`. Both use the same configured revision.

Copy the `EMBEDDING_*` entries from `.env.example` into your `.env` if it already
exists. `EMBEDDING_MODEL` and `EMBEDDING_REVISION` are required; the query and document
prefixes default to empty when omitted. The example selects BGE with its recommended
query prefix. Preserve the trailing space inside the quotes. Choose prefixes according
to the selected model's documentation.

Change model settings in `.env`, then restart the indexing/search process and rebuild
the index. The full configuration is stored with vectors so different models or
prefixes are never mixed during search. Until the rebuild, search won't match the
old index. Models must be compatible with Sentence Transformers; the current schema
requires 384 dimensions and rejects other sizes before indexing. A different vector
size still needs a database migration. These settings change retrieval embeddings,
not a future answer-generating LLM.

PostgreSQL stores the passage, audience, content-hash version, model identifier,
and vector. Search returns the top three passages with cosine similarity scores.
These scores are not calibrated confidence or proof that the KB answers a question.
Internal passages are included for the future support agent; this is a developer
CLI, not a customer-facing search endpoint.

After editing KB files, rerun the index command. It computes all embeddings first,
then replaces only `kb_chunks` in a transaction; a failure preserves the old index.
Removed articles disappear on successful rebuild. Run one rebuild at a time. Old
index versions are not archived in PostgreSQL; source changes remain in Git.

For the opt-in real-model retrieval checks, using the sample local database:

```sh
TEST_DATABASE_URL=postgresql://trailhaven:trailhaven_local@127.0.0.1:5433/trailhaven RUN_BGE_TESTS=1 uv run --env-file .env pytest
```

This embeds the real KB and verifies expected source IDs for care, discount, and
shipping questions in isolated schemas. Default tests do not load or download BGE.
Retrieval currently uses exact vector search; keyword/hybrid ranking, unknown-topic
handling, and answer generation remain later slices.

Read [buildlog.md](buildlog.md) for the handoff and [docs/decisions.md](docs/decisions.md)
for design rationale.
