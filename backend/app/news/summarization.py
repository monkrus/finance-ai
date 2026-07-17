import json
import logging
import uuid
from app.ai.gateway import AIGatewayService
from app.ai.models import PromptTemplate
from app.schemas.news import NewsSummarySchema

logger = logging.getLogger(__name__)

class SummarizationEngine:
    def __init__(self):
        self.gateway = AIGatewayService()
        self._ensure_prompt()

    def _ensure_prompt(self):
        self.gateway.prompt_manager.register(
            PromptTemplate(
                name="news_summary",
                template="""You are a strict JSON data extractor.
Summarize the financial news article.
Output MUST be valid JSON matching this schema:
{
    "executive_summary": "string",
    "key_takeaways": ["string"],
    "bullish_signals": ["string"],
    "bearish_signals": ["string"],
    "opportunities": ["string"],
    "risks": ["string"],
    "market_impact": "string"
}
Do not include any markdown tags or other text.
""",
                variables=[]
            )
        )

    async def summarize(self, headline: str, content: str) -> NewsSummarySchema:
        session_id = f"summary_{uuid.uuid4()}"
        text = f"HEADLINE: {headline}\nCONTENT: {content}"
        response = await self.gateway.chat(session_id, text, system_prompt_name="news_summary")
        try:
            clean_json = response.strip().strip("```json").strip("```").strip()
            data = json.loads(clean_json)
            return NewsSummarySchema(**data)
        except Exception as e:
            logger.error(f"Failed to parse summary JSON: {e}")
            return None
