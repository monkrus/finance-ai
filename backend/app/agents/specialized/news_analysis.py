from app.agents.base import BaseAgent
from app.agents.models import AgentConfig
from app.ai.gateway import AIGatewayService

class NewsAnalysisAgent(BaseAgent):
    def __init__(self, gateway: AIGatewayService):
        config = AgentConfig(
            name="news_analysis",
            description="News summarization, market impact, sentiment",
            system_prompt_name="agent_news_analysis",
            allowed_tools=["get_market_news", "get_stock_quote"],
            temperature=0.5
        )
        super().__init__(config, gateway)
