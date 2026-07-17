import pytest
import json
from app.ai.tool_registry import ToolRegistry
from app.ai.models import AITool
from app.core.exceptions import FinPilotException

@pytest.mark.asyncio
async def test_tool_registry_execute():
    registry = ToolRegistry()
    
    async def dummy_tool(symbol: str, count: int):
        return {"price": 100, "symbol": symbol, "count": count}
        
    tool = AITool(
        name="get_stock", 
        description="Get stock", 
        parameters={
            "type": "object", 
            "properties": {
                "symbol": {"type": "string"},
                "count": {"type": "integer"}
            }
        }
    )
    
    registry.register(tool, dummy_tool)
    
    result = await registry.execute_tool("get_stock", {"symbol": "AAPL", "count": 10})
    result_dict = json.loads(result)
    
    assert result_dict["price"] == 100
    assert result_dict["symbol"] == "AAPL"
    assert result_dict["count"] == 10

@pytest.mark.asyncio
async def test_tool_registry_error():
    registry = ToolRegistry()
    
    with pytest.raises(FinPilotException) as exc:
        await registry.execute_tool("non_existent_tool", {})
        
    assert exc.value.status_code == 400

@pytest.mark.asyncio
async def test_tool_registry_get_all_and_error():
    registry = ToolRegistry()
    
    async def bad_tool():
        raise ValueError("Tool broke")
        
    tool = AITool(name="bad", description="bad", parameters={})
    registry.register(tool, bad_tool)
    
    tools = registry.get_all_tools()
    assert len(tools) == 1
    assert tools[0].name == "bad"
    
    res = await registry.execute_tool("bad", {})
    assert "Error executing tool bad" in res
