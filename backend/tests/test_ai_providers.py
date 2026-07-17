import pytest
import os
from unittest.mock import AsyncMock, patch
from app.ai.providers.gemini import GeminiProvider
from app.ai.models import AIMessage, AITool
from app.core.exceptions import FinPilotException

@pytest.mark.asyncio
async def test_gemini_provider_generate_content():
    provider = GeminiProvider(api_key="test")
    
    # Mock google-genai Client
    with patch("app.ai.providers.gemini.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_response = AsyncMock()
        mock_response.text = "Mocked LLM Response"
        mock_response.usage_metadata.total_token_count = 15
        mock_response.function_calls = None
        
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        
        # Override provider client
        provider.client = mock_client
        
        messages = [AIMessage(role="user", content="Hello")]
        response = await provider.generate_content(messages=messages)
        
        assert response.content == "Mocked LLM Response"
        assert response.tokens_used == 15
        
@pytest.mark.asyncio
async def test_gemini_provider_error():
    provider = GeminiProvider(api_key="test")
    
    with patch("app.ai.providers.gemini.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_client.aio.models.generate_content.side_effect = Exception("Google Cloud Error")
        provider.client = mock_client
        
        messages = [AIMessage(role="user", content="Hello")]
        
        with pytest.raises(FinPilotException) as exc:
            await provider.generate_content(messages=messages)
            
        assert "Gemini API Error" in exc.value.message
        assert exc.value.status_code == 500

@pytest.mark.asyncio
async def test_gemini_provider_convert_messages_and_tools():
    provider = GeminiProvider(api_key="test")
    messages = [
        AIMessage(role="system", content="System 1"),
        AIMessage(role="system", content="System 2"),
        AIMessage(role="user", content="User msg"),
        AIMessage(role="tool", name="my_tool", content="Tool result")
    ]
    sys_inst, contents = provider._convert_messages(messages)
    assert sys_inst == "System 1\nSystem 2"
    assert len(contents) == 2
    assert contents[0].role == "user"
    assert contents[1].role == "user" # Tool response is mapped to user with function_response
    
    tools = [AITool(name="test", description="desc", parameters={"type": "object"})]
    gemini_tools = provider._convert_tools(tools)
    assert len(gemini_tools) == 1
    assert gemini_tools[0].function_declarations[0].name == "test"
    assert provider._convert_tools([]) is None

@pytest.mark.asyncio
async def test_gemini_provider_tool_call_response():
    provider = GeminiProvider(api_key="test")
    with patch("app.ai.providers.gemini.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        mock_response = AsyncMock()
        mock_response.text = None
        mock_response.usage_metadata.total_token_count = 10
        
        class MockFC:
            name = "get_stock"
            args = {"symbol": "AAPL"}
            
        mock_response.function_calls = [MockFC()]
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        provider.client = mock_client
        
        resp = await provider.generate_content(messages=[AIMessage(role="user", content="hi")])
        assert resp.content == ""
        assert resp.tokens_used == 10
        # Check raw_response.function_calls was checked (the provider checks it but doesn't store it parsed in AIResponse directly in this version, it's checked by Gateway)
        assert resp.raw_response.function_calls is not None

@pytest.mark.asyncio
async def test_gemini_provider_stream_success():
    provider = GeminiProvider(api_key="test")
    with patch("app.ai.providers.gemini.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        
        async def mock_stream(*args, **kwargs):
            class MockChunk:
                def __init__(self, t):
                    self.text = t
            yield MockChunk("Stream ")
            yield MockChunk("result")
            
        mock_client.aio.models.generate_content_stream = mock_stream
        provider.client = mock_client
        
        chunks = []
        async for c in provider.generate_stream(messages=[AIMessage(role="user", content="hi")]):
            chunks.append(c)
        assert chunks == ["Stream ", "result"]

@pytest.mark.asyncio
async def test_gemini_provider_stream_error():
    provider = GeminiProvider(api_key="test")
    with patch("app.ai.providers.gemini.genai.Client") as MockClient:
        mock_client = MockClient.return_value
        
        async def mock_stream(*args, **kwargs):
            raise Exception("Stream error")
            yield "never"
            
        mock_client.aio.models.generate_content_stream = mock_stream
        provider.client = mock_client
        
        with pytest.raises(FinPilotException) as exc:
            async for c in provider.generate_stream(messages=[]):
                pass
        assert "Streaming Error" in exc.value.message
