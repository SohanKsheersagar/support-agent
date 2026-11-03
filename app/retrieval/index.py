"""Rebuild the derived KB index atomically after all embeddings succeed."""

import json
import os

import psycopg

from app.retrieval.documents import Chunk, load_chunks
from app.retrieval.embeddings import Embedder


def replace_index(
    connection: psycopg.Connection, chunks: list[Chunk], vectors: list[list[float]],
    model_key: str,
) -> None:
    if not chunks or len(chunks) != len(vectors):
        raise ValueError("Each KB chunk must have exactly one embedding")
    with connection.transaction():
        connection.execute("DELETE FROM kb_chunks")
        with connection.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO kb_chunks
                    (source_id, title, text, version, audience, model, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s::public.vector)
            """, [
                (chunk.source_id, chunk.title, chunk.text, chunk.version,
                 chunk.audience, model_key, json.dumps(vector))
                for chunk, vector in zip(chunks, vectors, strict=True)
            ])


if __name__ == "__main__":
    chunks = load_chunks()
    encoder = Embedder()
    vectors = encoder.documents([f"{chunk.title}\n\n{chunk.text}" for chunk in chunks])
    with psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=5) as connection:
        replace_index(connection, chunks, vectors, encoder.key)
    print(f"Indexed {len(chunks)} KB articles with {encoder.key}")
