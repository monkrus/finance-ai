from app.agents.base import BaseAgent
from app.agents.models import AgentConfig
from app.ai.gateway import AIGatewayService

class PortfolioAdvisorAgent(BaseAgent):
    def __init__(self, gateway: AIGatewayService):
        config = AgentConfig(
            name="portfolio_advisor",
            description="Portfolio diversification, allocation suggestions",
            system_prompt_name="agent_portfolio_advisor",
            allowed_tools=[], # Portfolio tools not yet implemented
            temperature=0.6
        )
        super().__init__(config, gateway)
