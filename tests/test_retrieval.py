import os
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import psycopg
import pytest

from app.db.migrate import migrate
from app.retrieval.documents import load_chunks
from app.retrieval.embeddings import Embedder, EmbeddingConfig
from app.retrieval.index import replace_index
from app.retrieval.search import search_kb


def test_source_articles_are_complete_and_versioned():
    chunks = load_chunks()
    assert len(chunks) == 22
    assert len({chunk.source_id for chunk in chunks}) == len(chunks)
    care = next(chunk for chunk in chunks if chunk.source_id == "KB-CARE-001")
    assert "tennis balls" in care.text
    assert len(care.version) == 64
    assert next(c for c in chunks if c.source_id == "KB-REF-001").audience == "internal"


def test_document_edits_change_version(tmp_path):
    article = tmp_path / "KB-TEST-001.md"
    article.write_text("# Test\n\nAudience: public\n\nFirst policy.")
    before = load_chunks(tmp_path)[0].version
    article.write_text("# Test\n\nAudience: public\n\nUpdated policy.")
    assert load_chunks(tmp_path)[0].version != before


def test_invalid_or_empty_kb_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="No KB articles"):
        load_chunks(tmp_path)
    (tmp_path / "notes.md").write_text("Not a company article")
    with pytest.raises(ValueError, match="Invalid KB article"):
        load_chunks(tmp_path)


def test_embeddings_reject_silent_truncation():
    encoder = Embedder.__new__(Embedder)
    encoder.model = Mock()
    encoder.model.max_seq_length = 512
    encoder.model.tokenizer.encode.return_value = [1] * 513
    with pytest.raises(ValueError, match="exceeds model token limit"):
        encoder.embed(["Oversized text"])
    encoder.model.encode.assert_not_called()


def test_configuration_is_required_and_changes_index_identity(monkeypatch):
    monkeypatch.delenv("EMBEDDING_MODEL", raising=False)
    with pytest.raises(ValueError, match="Set EMBEDDING_MODEL"):
        EmbeddingConfig.from_env()
    monkeypatch.setenv("EMBEDDING_MODEL", "test-model")
    monkeypatch.setenv("EMBEDDING_REVISION", "revision-1")
    first = EmbeddingConfig.from_env()
    monkeypatch.setenv("EMBEDDING_REVISION", "revision-2")
    assert EmbeddingConfig.from_env().key != first.key
    monkeypatch.setenv("EMBEDDING_REVISION", "revision-1")
    monkeypatch.setenv("EMBEDDING_QUERY_PREFIX", "query: ")
    assert EmbeddingConfig.from_env().key != first.key


def test_configured_model_prefixes_and_dimensions(monkeypatch):
    monkeypatch.setenv("EMBEDDING_MODEL", "test-model")
    monkeypatch.setenv("EMBEDDING_REVISION", "revision-1")
    monkeypatch.setenv("EMBEDDING_QUERY_PREFIX", "query: ")
    monkeypatch.setenv("EMBEDDING_DOCUMENT_PREFIX", "passage: ")
    model = Mock()
    model.get_embedding_dimension.return_value = 384
    model.max_seq_length = 512
    model.tokenizer.encode.return_value = [1, 2]
    model.encode.return_value.tolist.return_value = [[0.0] * 384]
    factory = Mock(return_value=model)
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(
        SentenceTransformer=factory
    ))
    encoder = Embedder()
    factory.assert_called_once_with(
        "test-model", revision="revision-1", device="cpu", trust_remote_code=False
    )
    encoder.query("question")
    model.encode.assert_called_with(["query: question"], normalize_embeddings=True)
    encoder.documents(["policy"])
    model.encode.assert_called_with(["passage: policy"], normalize_embeddings=True)
    model.get_embedding_dimension.return_value = 768
    with pytest.raises(ValueError, match="384-dimensional"):
        Embedder()


def test_vector_index_search_and_failed_rebuild(database):
    migrate(database)
    chunks = load_chunks()[:2]
    first = [1.0] + [0.0] * 383
    second = [0.0, 1.0] + [0.0] * 382
    replace_index(database, chunks, [first, second], "test-model")
    encoder = Mock(spec=Embedder)
    encoder.query.return_value = first
    encoder.key = "test-model"
    results = search_kb(database, encoder, "Relevant policy", top_k=1)
    assert results[0]["source_id"] == chunks[0].source_id
    assert results[0]["version"] == chunks[0].version
    assert results[0]["score"] == pytest.approx(1.0)
    with pytest.raises(psycopg.errors.DataException):
        replace_index(database, chunks, [first, [1.0]], "test-model")
    assert database.execute("SELECT count(*) FROM kb_chunks").fetchone() == (2,)
    replace_index(database, chunks[:1], [first], "test-model")
    assert database.execute("SELECT count(*) FROM kb_chunks").fetchone() == (1,)
    database.execute("UPDATE kb_chunks SET model = 'different-model'")
    assert search_kb(database, encoder, "Relevant policy") == []


def test_invalid_search_does_not_embed():
    encoder = Mock(spec=Embedder)
    for query, top_k in [("", 3), ("Returns", 0), ("Returns", 6)]:
        with pytest.raises(ValueError):
            search_kb(Mock(), encoder, query, top_k)
    encoder.query.assert_not_called()


@pytest.mark.skipif(
    os.environ.get("RUN_BGE_TESTS") != "1",
    reason="Set RUN_BGE_TESTS=1 for real-model retrieval checks",
)
def test_bge_retrieves_expected_policies(database):
    migrate(database)
    chunks = load_chunks()
    encoder = Embedder()
    vectors = encoder.documents([f"{c.title}\n\n{c.text}" for c in chunks])
    assert all(len(vector) == 384 for vector in vectors)
    replace_index(database, chunks, vectors, encoder.key)
    for query, expected in [
        ("How do I wash my down sleeping bag?", "KB-CARE-001"),
        ("Can I get a student discount?", "KB-PRC-002"),
        ("My parcel tracking has stopped moving", "KB-SHIP-002"),
    ]:
        assert expected in {r["source_id"] for r in search_kb(database, encoder, query)}
