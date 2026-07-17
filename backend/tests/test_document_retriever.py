import pytest
from unittest.mock import AsyncMock
from app.document_intelligence.vector_store import InMemoryVectorStore
from app.document_intelligence.embedder import EmbedderInterface, GeminiEmbedder
from app.document_intelligence.retriever import HybridRetriever
from app.document_intelligence.models import DocumentChunk, DocumentMetadata
from app.ai.gateway import AIGatewayService

@pytest.fixture
def mock_gateway():
    gateway = AIGatewayService()
    mock_provider = AsyncMock()
    
    class MockResult:
        class Emb:
            values = [0.1, 0.2, 0.3]
        embeddings = [Emb()]
        
    mock_provider.client.aio.models.embed_content = AsyncMock(return_value=MockResult())
    gateway.provider = mock_provider
    return gateway

@pytest.mark.asyncio
async def test_embedder(mock_gateway):
    embedder = GeminiEmbedder(mock_gateway)
    emb = await embedder.embed_text("test")
    assert emb == [0.1, 0.2, 0.3]
    
    batch = await embedder.embed_batch(["test1", "test2"])
    assert len(batch) == 2
    assert batch[0] == [0.1, 0.2, 0.3]

@pytest.mark.asyncio
async def test_embedder_failure(mock_gateway):
    mock_gateway.provider.client.aio.models.embed_content = AsyncMock(side_effect=Exception("Failed"))
    embedder = GeminiEmbedder(mock_gateway)
    emb = await embedder.embed_text("test")
    assert emb == [0.0] * 768

@pytest.mark.asyncio
async def test_vector_store():
    store = InMemoryVectorStore()
    
    meta = DocumentMetadata(source="a", doc_type="10-K", ticker="AAPL")
    c1 = DocumentChunk(document_id="d1", text="revenue grew 10%", section_name="MD&A", metadata=meta, embedding=[1.0, 0.0])
    c2 = DocumentChunk(document_id="d1", text="we sell iPhones", section_name="Business Overview", metadata=meta, embedding=[0.0, 1.0])
    
    await store.add_chunks([c1, c2])
    
    # Semantic Search
    res = await store.semantic_search([1.0, 0.0], top_k=1)
    assert len(res) == 1
    assert res[0].id == c1.id
    
    # Semantic Search with invalid input
    res = await store.semantic_search([1.0], top_k=1) # Length mismatch
    assert len(res) == 1
    
    # Keyword Search
    res = await store.keyword_search("iphones", top_k=1)
    assert len(res) == 1
    assert res[0].id == c2.id
    
    # Metadata filter
    res = await store.keyword_search("revenue", top_k=5, metadata_filters={"section_name": "Business Overview"})
    assert len(res) == 0
    
    # Update and Delete
    await store.delete_document("d1")
    res = await store.semantic_search([1.0, 0.0], top_k=1)
    assert len(res) == 0
    
    c3 = DocumentChunk(document_id="d2", text="new chunk", section_name="General", metadata=meta, embedding=[1.0, 1.0])
    await store.update_document("d2", [c3])
    res = await store.keyword_search("new", top_k=1)
    assert len(res) == 1
    assert res[0].document_id == "d2"

@pytest.mark.asyncio
async def test_hybrid_retriever():
    store = InMemoryVectorStore()
    meta = DocumentMetadata(source="a", doc_type="10-K", ticker="AAPL")
    c1 = DocumentChunk(document_id="d1", text="revenue grew 10%", section_name="MD&A", metadata=meta, embedding=[1.0, 0.0])
    await store.add_chunks([c1])
    
    class MockEmbedder(EmbedderInterface):
        async def embed_text(self, text):
            return [1.0, 0.0]
        async def embed_batch(self, texts):
            return [[1.0, 0.0]]
            
    retriever = HybridRetriever(store, MockEmbedder())
    res = await retriever.search("revenue", top_k=1)
    
    assert len(res) == 1
    assert res[0].id == c1.id
