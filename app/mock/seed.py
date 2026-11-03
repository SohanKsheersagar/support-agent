"""Load fictional fixtures without overwriting existing rows."""

import os
from pathlib import Path

import psycopg


def seed(connection: psycopg.Connection) -> None:
    with connection.transaction():
        connection.execute(Path(__file__).with_suffix(".sql").read_text())


if __name__ == "__main__":
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5) as connection:
        seed(connection)
    print("Mock customers and orders loaded")
