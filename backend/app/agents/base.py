import logging
from typing import AsyncGenerator
from app.ai.gateway import AIGatewayService
from app.agents.models import AgentConfig
from app.core.exceptions import FinPilotException

logger = logging.getLogger(__name__)

class BaseAgent:
    """
    Abstract Base Class for Financial Agents.
    Encapsulates a specific configuration (tools, prompt, temperature)
    and executes via the standard AI Gateway.
    """
    def __init__(self, config: AgentConfig, gateway: AIGatewayService):
        self.config = config
        self.gateway = gateway
        
    def _get_namespaced_session(self, user_session_id: str) -> str:
        # Isolate memory by prefixing with agent name
        return f"{self.config.name}::{user_session_id}"

    async def chat(self, user_session_id: str, user_input: str) -> str:
        logger.info(f"Agent {self.config.name} handling request for session {user_session_id}")
        session_id = self._get_namespaced_session(user_session_id)
        
        # We can dynamically override the provider temperature if gateway supported it,
        # but for now, we pass the tools and prompt name.
        
        return await self.gateway.chat(
            session_id=session_id,
            user_input=user_input,
            system_prompt_name=self.config.system_prompt_name,
            allowed_tools=self.config.allowed_tools
        )

    async def chat_stream(self, user_session_id: str, user_input: str) -> AsyncGenerator[str, None]:
        logger.info(f"Agent {self.config.name} streaming request for session {user_session_id}")
        session_id = self._get_namespaced_session(user_session_id)
        
        async for chunk in self.gateway.chat_stream(
            session_id=session_id,
            user_input=user_input,
            system_prompt_name=self.config.system_prompt_name,
            allowed_tools=self.config.allowed_tools
        ):
            yield chunk
