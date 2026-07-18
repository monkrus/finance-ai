"""Multi-tenancy / tenant-isolation tests for the document RAG subsystem.

Verifies that document retrieval is strictly scoped by the owning user_id so
that one user can never retrieve another user's uploaded documents — both at
the vector-store/retriever layer and at the API boundary.
"""
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from main import app
from app.api.deps import get_current_user
from app.schemas.user import UserProfileResponse
from app.document_intelligence.models import DocumentChunk, DocumentMetadata, RAGResponse
from app.document_intelligence.vector_store import InMemoryVectorStore
from app.document_intelligence.retriever import HybridRetriever
import app.api.v1.documents as docs_mod


def _chunk(user_id: int, doc_id: str, text: str) -> DocumentChunk:
    meta = DocumentMetadata(source=f"{doc_id}.pdf", doc_type="10-K", ticker="AAPL", user_id=user_id)
    return DocumentChunk(
        document_id=doc_id,
        text=text,
        section_name="MD&A",
        metadata=meta,
        embedding=[1.0, 0.0],
    )


@pytest.mark.asyncio
async def test_vector_store_scopes_semantic_and_keyword_search_by_user():
    store = InMemoryVectorStore()
    await store.add_chunks([
        _chunk(1, "d1", "secret revenue numbers alpha"),
        _chunk(2, "d2", "secret revenue numbers beta"),
    ])

    # Semantic search scoped to user 1 must not surface user 2's chunk.
    sem = await store.semantic_search([1.0, 0.0], top_k=10, metadata_filters={"user_id": 1})
    assert {c.document_id for c in sem} == {"d1"}

    # Keyword search scoped to user 2 must not surface user 1's chunk.
    kw = await store.keyword_search("secret revenue", top_k=10, metadata_filters={"user_id": 2})
    assert {c.document_id for c in kw} == {"d2"}

    # Without a user_id filter both are visible — proving isolation depends on
    # the enforced scope (which the API layer always injects).
    both = await store.semantic_search([1.0, 0.0], top_k=10)
    assert {c.document_id for c in both} == {"d1", "d2"}


@pytest.mark.asyncio
async def test_hybrid_retriever_respects_user_scope():
    store = InMemoryVectorStore()
    await store.add_chunks([
        _chunk(1, "d1", "secret revenue numbers alpha"),
        _chunk(2, "d2", "secret revenue numbers beta"),
    ])
    embedder = AsyncMock()
    embedder.embed_text = AsyncMock(return_value=[1.0, 0.0])
    retriever = HybridRetriever(store, embedder)

    results = await retriever.search("secret revenue", top_k=10, metadata_filters={"user_id": 1})
    assert results, "expected the owning user's chunk to be retrieved"
    assert all(c.metadata.user_id == 1 for c in results)
    assert "d2" not in {c.document_id for c in results}


@pytest.mark.parametrize("user_id", [5, 6])
def test_query_endpoint_always_scopes_to_authenticated_user(user_id):
    """The /documents/query endpoint must inject the caller's user_id filter,
    regardless of what the client sends, so cross-user access is impossible."""
    async def override_user():
        return UserProfileResponse(id=user_id, email=f"u{user_id}@example.com", is_active=True, is_verified=True)

    captured = {}

    async def fake_query(query, top_k=5, metadata_filters=None):
        captured["filters"] = metadata_filters
        return RAGResponse(answer="ok", citations=[], confidence_score=1.0)

    original_query = docs_mod.rag_engine.query
    docs_mod.rag_engine.query = fake_query
    app.dependency_overrides[get_current_user] = override_user
    try:
        client = TestClient(app)
        res = client.post("/api/v1/documents/query", json={"query": "anything", "ticker": "AAPL"})
        assert res.status_code == 200
        assert captured["filters"]["user_id"] == user_id
    finally:
        docs_mod.rag_engine.query = original_query
        app.dependency_overrides.pop(get_current_user, None)
