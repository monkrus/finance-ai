import pytest
from unittest.mock import AsyncMock, patch
from app.ai.gateway import AIGatewayService
from app.ai.models import AIMessage, AIResponse, AITool
from app.core.exceptions import FinPilotException

@pytest.mark.asyncio
async def test_chat_success():
    service = AIGatewayService()
    
    # Mock Provider
    mock_response = AIResponse(content="Hello there!", tokens_used=10)
    service.provider.generate_content = AsyncMock(return_value=mock_response)
    
    # Run
    result = await service.chat("session_123", "Hello AI")
    
    # Assert
    assert result == "Hello there!"
    service.provider.generate_content.assert_called_once()
    
    # Assert memory was updated
    history = await service.memory_manager.get_history("session_123")
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello AI"
    assert history[1].role == "model"
    assert history[1].content == "Hello there!"

@pytest.mark.asyncio
async def test_chat_error_recovery():
    service = AIGatewayService()
    service.provider.generate_content = AsyncMock(side_effect=Exception("API limit"))
    
    result = await service.chat("session_error", "Hello")
    # Degrades gracefully with a user-facing message and does NOT leak the raw
    # internal error detail ("API limit") to the client.
    assert "temporarily unavailable" in result
    assert "API limit" not in result

@pytest.mark.asyncio
async def test_chat_tool_execution():
    service = AIGatewayService()
    
    # Register a mock tool
    async def dummy_tool(symbol: str):
        return f"Price of {symbol} is 150.00"
        
    tool = AITool(name="get_price", description="Get price", parameters={"type": "object", "properties": {"symbol": {"type": "string"}}})
    service.tool_registry.register(tool, dummy_tool)
    
    # First response asks for tool call
    class MockFC:
        name = "get_price"
        args = {"symbol": "AAPL"}
        
    class MockRawResponse:
        function_calls = [MockFC()]
        
    mock_response_1 = AIResponse(content="", raw_response=MockRawResponse())
    mock_response_2 = AIResponse(content="The price is 150.00")
    
    service.provider.generate_content = AsyncMock(side_effect=[mock_response_1, mock_response_2])
    
    result = await service.chat("session_tools", "What is AAPL price?")
    assert result == "The price is 150.00"
    
    # Verify history contains tool response
    history = await service.memory_manager.get_history("session_tools")
    # We should have User -> Model (Final) because tool history isn't saved in final memory to save space, or wait, it IS saved!
    # Ah, I didn't save the tool call interaction into Redis memory inside `gateway.py`, I only appended to `provider_messages`.
    # Let's check `history`:
    assert len(history) == 2
    assert history[0].content == "What is AAPL price?"
    assert history[1].content == "The price is 150.00"

@pytest.mark.asyncio
async def test_chat_stream():
    service = AIGatewayService()
    
    async def mock_stream(*args, **kwargs):
        yield "Chunk1"
        yield "Chunk2"
        
    service.provider.generate_stream = mock_stream
    
    chunks = []
    async for chunk in service.chat_stream("session_stream", "Hi"):
        chunks.append(chunk)
        
    assert chunks == ["Chunk1", "Chunk2"]
    
    
    # Check memory
    history = await service.memory_manager.get_history("session_stream")
    assert history[1].content == "Chunk1Chunk2"

@pytest.mark.asyncio
async def test_chat_tool_execution_error():
    service = AIGatewayService()
    
    # Register a mock tool that fails
    async def bad_tool(symbol: str):
        raise ValueError("API Offline")
        
    tool = AITool(name="get_price", description="Get price", parameters={"type": "object", "properties": {"symbol": {"type": "string"}}})
    service.tool_registry.register(tool, bad_tool)
    
    class MockFC:
        name = "get_price"
        args = {"symbol": "AAPL"}
        
    class MockRawResponse:
        function_calls = [MockFC()]
        
    mock_response_1 = AIResponse(content="", raw_response=MockRawResponse())
    mock_response_2 = AIResponse(content="I could not fetch the price.")
    
    service.provider.generate_content = AsyncMock(side_effect=[mock_response_1, mock_response_2])
    
    result = await service.chat("session_tools_err", "What is AAPL price?")
    assert result == "I could not fetch the price."

@pytest.mark.asyncio
async def test_chat_stream_error():
    service = AIGatewayService()
    
    async def mock_stream(*args, **kwargs):
        yield "Chunk1"
        raise ValueError("Stream failed")
        
    service.provider.generate_stream = mock_stream
    
    chunks = []
    async for chunk in service.chat_stream("session_stream_err", "Hi"):
        chunks.append(chunk)
        
    assert len(chunks) == 2
    assert chunks[0] == "Chunk1"
    # Streaming degrades to the graceful fallback without leaking the raw error.
    assert "temporarily unavailable" in chunks[1]
    assert "Stream failed" not in chunks[1]
