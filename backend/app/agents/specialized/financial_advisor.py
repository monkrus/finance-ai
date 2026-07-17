from app.agents.base import BaseAgent
from app.agents.models import AgentConfig
from app.ai.gateway import AIGatewayService

class FinancialAdvisorAgent(BaseAgent):
    def __init__(self, gateway: AIGatewayService):
        config = AgentConfig(
            name="financial_advisor",
            description="Investment guidance and goal planning",
            system_prompt_name="agent_financial_advisor",
            allowed_tools=["get_company_profile", "get_stock_quote", "calculator"],
            temperature=0.7
        )
        super().__init__(config, gateway)
