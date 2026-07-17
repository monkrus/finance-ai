from app.agents.base import BaseAgent
from app.agents.models import AgentConfig
from app.ai.gateway import AIGatewayService

class FinanceTutorAgent(BaseAgent):
    def __init__(self, gateway: AIGatewayService):
        config = AgentConfig(
            name="finance_tutor",
            description="Explain finance concepts, DCF, accounting",
            system_prompt_name="agent_finance_tutor",
            allowed_tools=[], # No tools needed for purely educational agent
            temperature=0.8
        )
        super().__init__(config, gateway)
