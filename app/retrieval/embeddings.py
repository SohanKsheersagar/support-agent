"""Local embeddings configured through environment variables."""

from dataclasses import dataclass
import json
import os


@dataclass(frozen=True)
class EmbeddingConfig:
    model: str
    revision: str
    query_prefix: str
    document_prefix: str

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        model = os.environ.get("EMBEDDING_MODEL", "").strip()
        revision = os.environ.get("EMBEDDING_REVISION", "").strip()
        if not model or not revision:
            raise ValueError("Set EMBEDDING_MODEL and EMBEDDING_REVISION in .env")
        return cls(model, revision, os.environ.get("EMBEDDING_QUERY_PREFIX", ""),
                   os.environ.get("EMBEDDING_DOCUMENT_PREFIX", ""))

    @property
    def key(self) -> str:
        return json.dumps([self.model, self.revision, self.query_prefix,
                           self.document_prefix, "normalized-v1"])


class Embedder:
    def __init__(self):
        self.config = EmbeddingConfig.from_env()
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(
            self.config.model, revision=self.config.revision,
            device="cpu", trust_remote_code=False
        )
        if self.model.get_embedding_dimension() != 384:
            raise ValueError("The KB schema requires 384-dimensional embeddings; migrate it before changing dimensions")

    @property
    def key(self) -> str:
        return self.config.key

    def embed(self, texts: list[str]) -> list[list[float]]:
        for text in texts:
            if not text.strip():
                raise ValueError("Cannot embed empty text")
            if len(self.model.tokenizer.encode(text)) > self.model.max_seq_length:
                raise ValueError("Text exceeds model token limit; split the article or shorten the query")
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def documents(self, texts: list[str]) -> list[list[float]]:
        return self.embed([self.config.document_prefix + text for text in texts])

    def query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Search query cannot be empty")
        return self.embed([self.config.query_prefix + text])[0]
