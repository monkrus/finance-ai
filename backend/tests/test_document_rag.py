import pytest
from unittest.mock import AsyncMock
from app.document_intelligence.engine import RAGEngine
from app.document_intelligence.retriever import HybridRetriever
from app.document_intelligence.models import DocumentChunk, DocumentMetadata
from app.ai.gateway import AIGatewayService

@pytest.fixture
def mock_retriever():
    retriever = AsyncMock(spec=HybridRetriever)
    meta = DocumentMetadata(source="a", doc_type="10-K", ticker="AAPL")
    c1 = DocumentChunk(document_id="d1", text="revenue grew 10%", section_name="MD&A", metadata=meta)
    c1.id = "mock_chunk_id"
    retriever.search = AsyncMock(return_value=[c1])
    return retriever

@pytest.fixture
def mock_gateway():
    gateway = AIGatewayService()
    class MockResponse:
        text = '{"answer": "Revenue grew by 10%.", "citations": ["mock_chunk_id"], "confidence_score": 0.99}'
    gateway.provider._execute_generate = AsyncMock(return_value=MockResponse())
    return gateway

@pytest.mark.asyncio
async def test_rag_engine_success(mock_retriever, mock_gateway):
    engine = RAGEngine(mock_retriever, mock_gateway)
    
    res = await engine.query("How much did revenue grow?", top_k=1)
    
    assert res.answer == "Revenue grew by 10%."
    assert res.confidence_score == 0.99
    assert len(res.citations) == 1
    assert res.citations[0].chunk_id == "mock_chunk_id"
    assert "revenue grew 10%" in res.citations[0].text_snippet

@pytest.mark.asyncio
async def test_rag_engine_no_docs(mock_retriever, mock_gateway):
    mock_retriever.search = AsyncMock(return_value=[])
    engine = RAGEngine(mock_retriever, mock_gateway)
    
    res = await engine.query("How much did revenue grow?", top_k=1)
    
    assert res.answer == "No relevant documents found."
    assert res.confidence_score == 0.0
    assert len(res.citations) == 0
    
@pytest.mark.asyncio
async def test_rag_engine_hallucination_prevention(mock_retriever, mock_gateway):
    # If chunks are found but answer is not in them
    engine = RAGEngine(mock_retriever, mock_gateway)
    
    class MockResponse:
        text = '{"answer": "Information not found in the provided documents.", "citations": [], "confidence_score": 0.0}'
    mock_gateway.provider._execute_generate = AsyncMock(return_value=MockResponse())
    
    res = await engine.query("Who is the CEO?", top_k=1)
    assert res.answer == "Information not found in the provided documents."
    assert len(res.citations) == 0

@pytest.mark.asyncio
async def test_rag_engine_generation_error(mock_retriever, mock_gateway):
    mock_gateway.provider._execute_generate = AsyncMock(side_effect=Exception("API Error"))
    engine = RAGEngine(mock_retriever, mock_gateway)
    
    res = await engine.query("How much did revenue grow?", top_k=1)
    
    assert "Failed to generate answer" in res.answer
    assert res.confidence_score == 0.0
    assert len(res.citations) == 0
