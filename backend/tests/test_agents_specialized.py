import pytest
from unittest.mock import AsyncMock
from app.ai.gateway import AIGatewayService
from app.agents.specialized.financial_advisor import FinancialAdvisorAgent
from app.agents.specialized.stock_research import StockResearchAgent
from app.agents.specialized.news_analysis import NewsAnalysisAgent
from app.agents.specialized.portfolio_advisor import PortfolioAdvisorAgent
from app.agents.specialized.finance_tutor import FinanceTutorAgent
from app.agents.specialized.research_assistant import ResearchAssistantAgent

@pytest.fixture
def mock_gateway():
    gateway = AIGatewayService()
    gateway.chat = AsyncMock(return_value="Mock Chat Response")
    
    async def mock_stream(*args, **kwargs):
        yield "StreamChunk"
    gateway.chat_stream = mock_stream
    return gateway

@pytest.mark.asyncio
@pytest.mark.parametrize("agent_class, expected_name", [
    (FinancialAdvisorAgent, "financial_advisor"),
    (StockResearchAgent, "stock_research"),
    (NewsAnalysisAgent, "news_analysis"),
    (PortfolioAdvisorAgent, "portfolio_advisor"),
    (FinanceTutorAgent, "finance_tutor"),
    (ResearchAssistantAgent, "research_assistant"),
])
async def test_specialized_agents(mock_gateway, agent_class, expected_name):
    agent = agent_class(mock_gateway)
    assert agent.config.name == expected_name
    
    # Test chat
    res = await agent.chat("sess1", "Hello")
    assert res == "Mock Chat Response"
    mock_gateway.chat.assert_called_once()
    
    # Test stream
    chunks = []
    async for chunk in agent.chat_stream("sess1", "Hello"):
        chunks.append(chunk)
    assert chunks == ["StreamChunk"]
