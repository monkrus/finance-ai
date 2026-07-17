import json
import logging
from app.ai.gateway import AIGatewayService
from app.ai.models import PromptTemplate
from app.schemas.news import NewsSentimentSchema
import uuid

logger = logging.getLogger(__name__)

class SentimentEngine:
    def __init__(self):
        self.gateway = AIGatewayService()
        self._ensure_prompt()

    def _ensure_prompt(self):
        self.gateway.prompt_manager.register(
            PromptTemplate(
                name="news_sentiment",
                template="""You are a strict JSON data extractor.
Analyze the sentiment of the following financial news article.
Output MUST be valid JSON matching this schema:
{
    "label": "Positive" | "Neutral" | "Negative",
    "score": float (-1.0 to 1.0),
    "confidence": float (0.0 to 1.0),
    "reasoning": "brief explanation"
}
Do not include any markdown tags or other text.
""",
                variables=[]
            )
        )

    async def analyze(self, headline: str, content: str) -> NewsSentimentSchema:
        session_id = f"sentiment_{uuid.uuid4()}"
        text = f"HEADLINE: {headline}\nCONTENT: {content}"
        
        response = await self.gateway.chat(
            session_id=session_id,
            user_input=text,
            system_prompt_name="news_sentiment"
        )
        
        try:
            # Clean up markdown if AI Gateway returns it
            clean_json = response.strip().strip("```json").strip("```").strip()
            data = json.loads(clean_json)
            return NewsSentimentSchema(**data)
        except Exception as e:
            logger.error(f"Failed to parse sentiment JSON: {e}")
            return None
