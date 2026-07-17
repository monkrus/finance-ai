import json
import logging
from typing import AsyncGenerator
from google.genai import types

from app.ai.gateway import AIGatewayService
from app.agents.specialized.financial_advisor import FinancialAdvisorAgent
from app.agents.specialized.stock_research import StockResearchAgent
from app.agents.specialized.news_analysis import NewsAnalysisAgent
from app.agents.specialized.portfolio_advisor import PortfolioAdvisorAgent
from app.agents.specialized.finance_tutor import FinanceTutorAgent
from app.agents.specialized.research_assistant import ResearchAssistantAgent
from app.ai.models import AIMessage

logger = logging.getLogger(__name__)

class AgentRouter:
    def __init__(self, gateway: AIGatewayService):
        self.gateway = gateway
        
        # Instantiate agents
        self.agents = {
            "FINANCIAL_ADVISOR": FinancialAdvisorAgent(gateway),
            "STOCK_RESEARCH": StockResearchAgent(gateway),
            "NEWS_ANALYSIS": NewsAnalysisAgent(gateway),
            "PORTFOLIO_ADVISOR": PortfolioAdvisorAgent(gateway),
            "FINANCE_TUTOR": FinanceTutorAgent(gateway),
            "RESEARCH_ASSISTANT": ResearchAssistantAgent(gateway)
        }
        
    async def _detect_intent(self, user_input: str) -> str:
        """
        Uses a zero-shot prompt to classify the user's intent into an agent category.
        """
        try:
            # We want a very fast, single-turn classification without tools or history
            system_prompt = self.gateway.prompt_manager.render("agent_router_intent", user_input=user_input)
            
            # Configure Gemini for JSON output
            config = types.GenerateContentConfig(
                temperature=0.1, # Low temp for deterministic routing
                response_mime_type="application/json",
            )
            
            # Use gateway's provider directly for a low-level call
            res = await self.gateway.provider._execute_generate(
                contents=[system_prompt],
                config=config
            )
            
            if not res or not res.text:
                return "RESEARCH_ASSISTANT"
                
            data = json.loads(res.text)
            target = data.get("agent", "RESEARCH_ASSISTANT")
            confidence = data.get("confidence", 0.0)
            
            if confidence < 0.5 or target not in self.agents:
                logger.warning(f"Low confidence ({confidence}) or unknown target ({target}). Defaulting to RESEARCH_ASSISTANT.")
                return "RESEARCH_ASSISTANT"
                
            logger.info(f"Router classified intent: {target} (Confidence: {confidence})")
            return target
            
        except Exception as e:
            logger.error(f"Intent detection failed: {e}. Defaulting to RESEARCH_ASSISTANT.")
            return "RESEARCH_ASSISTANT"

    async def chat(self, session_id: str, user_input: str) -> str:
        target_agent_name = await self._detect_intent(user_input)
        agent = self.agents[target_agent_name]
        return await agent.chat(session_id, user_input)

    async def chat_stream(self, session_id: str, user_input: str) -> AsyncGenerator[str, None]:
        target_agent_name = await self._detect_intent(user_input)
        agent = self.agents[target_agent_name]
        
        # In a real app we might prepend a message indicating which agent took over
        yield f"[Routed to {agent.config.name}]\n\n"
        
        async for chunk in agent.chat_stream(session_id, user_input):
            yield chunk
