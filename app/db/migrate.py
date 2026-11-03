"""Apply pending SQL migrations atomically: python -m app.db.migrate."""

import os
from pathlib import Path

import psycopg


def migrate(connection: psycopg.Connection) -> None:
    # shortcut: single-operator local runner; use migration tooling before shared deployments.
    with connection.transaction():
        connection.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                name text PRIMARY KEY,
                applied_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        applied = {
            row[0] for row in connection.execute("SELECT name FROM schema_migrations")
        }
        for path in sorted(Path(__file__).with_name("migrations").glob("*.sql")):
            if path.name not in applied:
                connection.execute(path.read_text())
                connection.execute(
                    "INSERT INTO schema_migrations (name) VALUES (%s)", (path.name,)
                )


if __name__ == "__main__":
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5) as connection:
        migrate(connection)
    print("Database migrations applied")
