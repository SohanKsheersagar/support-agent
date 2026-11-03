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
