"""Read-only PostgreSQL connectivity check: python -m app.db.check."""

import os

import psycopg


def check_database() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("Set DATABASE_URL before checking the database.")
    with psycopg.connect(database_url, connect_timeout=5) as connection:
        connection.execute("SELECT 1").fetchone()


if __name__ == "__main__":
    check_database()
    print("PostgreSQL connection OK")
