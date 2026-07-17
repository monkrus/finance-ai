import logging
from typing import Dict, Callable, List, Any
from app.ai.models import AITool
from app.core.exceptions import FinPilotException
import json

logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Framework to register and execute external tools for Function Calling.
    """
    def __init__(self):
        self._tools: Dict[str, AITool] = {}
        self._callbacks: Dict[str, Callable] = {}

    def register(self, tool: AITool, callback: Callable):
        self._tools[tool.name] = tool
        self._callbacks[tool.name] = callback
        logger.debug(f"Registered tool: {tool.name}")

    def get_all_tools(self) -> List[AITool]:
        return list(self._tools.values())

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self._callbacks:
            raise FinPilotException(message=f"Tool {name} is not registered.", status_code=400)
        
        callback = self._callbacks[name]
        try:
            # We assume callbacks are async
            result = await callback(**args)
            if isinstance(result, (dict, list)):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}")
            return f"Error executing tool {name}: {str(e)}"
