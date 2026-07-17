import pytest
from unittest.mock import AsyncMock, patch
from app.agents.router import AgentRouter
from app.ai.gateway import AIGatewayService

@pytest.fixture
def mock_gateway():
    gateway = AIGatewayService()
    gateway.prompt_manager.register = lambda x: None
    gateway.prompt_manager.render = lambda name, **kwargs: "Mock Prompt"
    
    class MockResponse:
        def __init__(self, text):
            self.text = text
            
    gateway.provider._execute_generate = AsyncMock(return_value=MockResponse('{"agent": "FINANCIAL_ADVISOR", "confidence": 0.9}'))
    return gateway

@pytest.mark.asyncio
async def test_agent_router_intent_detect_success(mock_gateway):
    router = AgentRouter(mock_gateway)
    target = await router._detect_intent("How do I invest 10k?")
    assert target == "FINANCIAL_ADVISOR"

@pytest.mark.asyncio
async def test_agent_router_intent_detect_low_confidence(mock_gateway):
    class MockResponse:
        text = '{"agent": "FINANCIAL_ADVISOR", "confidence": 0.4}'
    mock_gateway.provider._execute_generate = AsyncMock(return_value=MockResponse())
    
    router = AgentRouter(mock_gateway)
    target = await router._detect_intent("What is pizza?")
    assert target == "RESEARCH_ASSISTANT"
    
@pytest.mark.asyncio
async def test_agent_router_intent_detect_invalid_agent(mock_gateway):
    class MockResponse:
        text = '{"agent": "FAKE_AGENT", "confidence": 0.9}'
    mock_gateway.provider._execute_generate = AsyncMock(return_value=MockResponse())
    
    router = AgentRouter(mock_gateway)
    target = await router._detect_intent("Input")
    assert target == "RESEARCH_ASSISTANT"

@pytest.mark.asyncio
async def test_agent_router_intent_detect_none(mock_gateway):
    mock_gateway.provider._execute_generate = AsyncMock(return_value=None)
    router = AgentRouter(mock_gateway)
    target = await router._detect_intent("Input")
    assert target == "RESEARCH_ASSISTANT"
    
@pytest.mark.asyncio
async def test_agent_router_intent_detect_exception(mock_gateway):
    mock_gateway.provider._execute_generate = AsyncMock(side_effect=Exception("API offline"))
    router = AgentRouter(mock_gateway)
    target = await router._detect_intent("Input")
    assert target == "RESEARCH_ASSISTANT"

@pytest.mark.asyncio
async def test_agent_router_chat(mock_gateway):
    router = AgentRouter(mock_gateway)
    
    # Mock the specific agent
    router.agents["FINANCIAL_ADVISOR"].chat = AsyncMock(return_value="Advisor Response")
    
    res = await router.chat("sess1", "Input")
    assert res == "Advisor Response"

@pytest.mark.asyncio
async def test_agent_router_chat_stream(mock_gateway):
    router = AgentRouter(mock_gateway)
    
    async def mock_stream(*args, **kwargs):
        yield "Stream1"
        yield "Stream2"
        
    router.agents["FINANCIAL_ADVISOR"].chat_stream = mock_stream
    
    chunks = []
    async for chunk in router.chat_stream("sess1", "Input"):
        chunks.append(chunk)
        
    assert chunks[0].startswith("[Routed to")
    assert chunks[1] == "Stream1"
    assert chunks[2] == "Stream2"
