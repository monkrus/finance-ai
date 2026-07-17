from app.agents.base import BaseAgent
from app.agents.models import AgentConfig
from app.ai.gateway import AIGatewayService

class StockResearchAgent(BaseAgent):
    def __init__(self, gateway: AIGatewayService):
        config = AgentConfig(
            name="stock_research",
            description="Company analysis, fundamentals, statements, ratios",
            system_prompt_name="agent_stock_research",
            allowed_tools=[
                "get_company_profile", "get_stock_quote", 
                "get_financial_ratios"
            ],
            temperature=0.4
        )
        super().__init__(config, gateway)
