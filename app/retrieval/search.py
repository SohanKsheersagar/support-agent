"""Retrieve policy passages, not generated answers."""

import argparse
import json
import os

import psycopg
from psycopg.rows import dict_row

from app.retrieval.embeddings import Embedder


def search_kb(
    connection: psycopg.Connection, encoder: Embedder, query: str, top_k: int = 3
) -> list[dict]:
    if not query.strip():
        raise ValueError("Search query cannot be empty")
    if not 1 <= top_k <= 5:
        raise ValueError("top_k must be between 1 and 5")
    vector = json.dumps(encoder.query(query))
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute("""
            SELECT source_id, title, text, version, audience,
                   1 - (embedding OPERATOR(public.<=>) %s::public.vector) AS score
            FROM kb_chunks
            WHERE model = %s
            ORDER BY embedding OPERATOR(public.<=>) %s::public.vector, source_id
            LIMIT %s
        """, (vector, encoder.key, vector, top_k))
        return cursor.fetchall()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query")
    args = parser.parse_args()
    encoder = Embedder()
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5) as connection:
        print(json.dumps(search_kb(connection, encoder, args.query), indent=2))
