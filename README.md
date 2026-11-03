# Trailhaven support agent

A learning project building a customer-support agent for a fictional outdoor retailer.
The MVP will draft replies for human review and escalate risky cases. It currently
contains PostgreSQL setup, the first business tables, and fictional seed data.

## Local setup

Install Python 3.12, [uv](https://docs.astral.sh/uv/), and Docker with Compose.
Start Docker Desktop (or your Docker engine) before running these commands:

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
knowledge pack stays there as a reference. `kb/` is reserved for versioned company
policies, FAQs, and tone articles the agent will retrieve by source ID. It is still
empty; splitting and indexing the pack is a later implementation step.

Read [buildlog.md](buildlog.md) for the handoff and [docs/decisions.md](docs/decisions.md)
for design rationale.
