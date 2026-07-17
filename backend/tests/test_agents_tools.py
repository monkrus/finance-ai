import pytest
from app.agents.tools import evaluate_math, register_all_tools
from app.ai.tool_registry import ToolRegistry
from unittest.mock import AsyncMock

def test_evaluate_math():
    assert evaluate_math("100 * 1.05 ** 10") == str(100 * 1.05 ** 10)
    assert evaluate_math("-10 + 5 / 2") == "-7.5"
    assert "Unsupported constant" in evaluate_math("'string' + 'test'")
    assert "Math Evaluation Error" in evaluate_math("import os")
    
@pytest.mark.asyncio
async def test_register_all_tools():
    registry = ToolRegistry()
    md_service = AsyncMock()
    
    md_service.get_company_profile.return_value = AsyncMock(model_dump=lambda: {"prof": "1"})
    md_service.get_quote.return_value = AsyncMock(model_dump=lambda: {"quote": "2"})
    md_service.get_market_news.return_value = [AsyncMock(model_dump=lambda: {"news": "3"})]
    md_service.get_financial_ratios.return_value = [AsyncMock(model_dump=lambda: {"ratio": "4"})]
    
    register_all_tools(registry, md_service)
    
    tools = registry.get_all_tools()
    assert len(tools) == 15
    
    # Execute them
    assert await registry.execute_tool("calculator", {"expression": "2+2"}) == "4"
    assert await registry.execute_tool("get_company_profile", {"ticker": "AAPL"}) == '{"prof": "1"}'
    assert await registry.execute_tool("get_stock_quote", {"ticker": "AAPL"}) == '{"quote": "2"}'
    assert await registry.execute_tool("get_market_news", {"ticker": "AAPL", "limit": 1}) == '[{"news": "3"}]'
    assert await registry.execute_tool("get_financial_ratios", {"ticker": "AAPL"}) == '[{"ratio": "4"}]'

@pytest.mark.asyncio
async def test_register_all_tools_none():
    registry = ToolRegistry()
    md_service = AsyncMock()
    md_service.get_company_profile.return_value = None
    md_service.get_quote.return_value = None
    
    register_all_tools(registry, md_service)
    
    assert await registry.execute_tool("get_company_profile", {"ticker": "AAPL"}) == '{"error": "Not found"}'
    assert await registry.execute_tool("get_stock_quote", {"ticker": "AAPL"}) == '{"error": "Not found"}'
