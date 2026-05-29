"""Vector store for semantic retrieval.

Stores text chunks with their embeddings and supports approximate nearest
neighbor (ANN) search for context retrieval.

Current backend: brute-force cosine similarity in-memory (dev only).
Future backends: Qdrant, Pinecone, ChromaDB — via Protocol interface.

TODO: Integrate embedding model (e.g., OpenAI, Cohere, or local sentence-transformers).
TODO: Implement QdrantVectorStore for production.
TODO: Add metadata filtering (by run_id, branch_id, etc.).
"""

from __future__ import annotations

import logging
import math
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VectorDocument(BaseModel):
    """A single indexed document with embedding."""

    id: str
    text: str
    embedding: list[float] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InMemoryVectorStore:
    """Brute-force cosine similarity search over in-memory documents.

    O(n) search — not suitable for large corpora. Used for dev/testing only.
    """

    def __init__(self) -> None:
        self._documents: dict[str, VectorDocument] = {}

    async def upsert(self, doc: VectorDocument) -> None:
        """Insert or update a document."""
        self._documents[doc.id] = doc
        logger.debug("VectorStore: upserted doc=%s", doc.id)

    async def search(self, query_embedding: list[float], top_k: int = 5) -> list[VectorDocument]:
        """Return top_k documents most similar to query_embedding.

        TODO: Replace with ANN index (HNSW) for sub-linear search.
        """
        if not self._documents:
            return []

        scores: list[tuple[float, VectorDocument]] = []
        for doc in self._documents.values():
            if doc.embedding:
                score = self._cosine_similarity(query_embedding, doc.embedding)
                scores.append((score, doc))

        scores.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scores[:top_k]]

    async def get(self, doc_id: str) -> VectorDocument | None:
        """Retrieve a document by ID."""
        return self._documents.get(doc_id)

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    @property
    def document_count(self) -> int:
        return len(self._documents)
