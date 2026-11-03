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
