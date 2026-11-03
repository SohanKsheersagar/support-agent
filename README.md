# Trailhaven support agent

A learning project building a customer-support agent for a fictional outdoor retailer.
The MVP will draft replies for human review and escalate risky cases. It currently
contains only the PostgreSQL development setup and a read-only connection check.

## Local setup

Install Python 3.12, [uv](https://docs.astral.sh/uv/), and Docker with Compose.
Start Docker Desktop (or your Docker engine) before running these commands:

```sh
cp .env.example .env
uv sync --locked
docker compose up -d --wait db
uv run --env-file .env python -m app.db.check
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
database password. There are no application tables yet.

Read [buildlog.md](buildlog.md) for the handoff and [docs/decisions.md](docs/decisions.md)
for design rationale.
