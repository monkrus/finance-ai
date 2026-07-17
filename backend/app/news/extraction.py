import json
import logging
import uuid
from typing import List
from app.ai.gateway import AIGatewayService
from app.ai.models import PromptTemplate
from app.schemas.news import NewsEntitySchema, NewsEventSchema

logger = logging.getLogger(__name__)

class EntityEngine:
    def __init__(self):
        self.gateway = AIGatewayService()
        self._ensure_prompt()

    def _ensure_prompt(self):
        self.gateway.prompt_manager.register(
            PromptTemplate(
                name="news_entity",
                template="""You are a strict JSON data extractor.
Extract financial entities (Companies, Tickers, CEOs, Products, Industries, Countries, Exchanges, Regulators, Institutions, Competitors) from this news.
Output MUST be valid JSON as an array of objects matching this schema:
[
  {
    "entity_type": "string",
    "entity_name": "string"
  }
]
Do not include any markdown tags or other text.
""",
                variables=[]
            )
        )

    async def extract(self, headline: str, content: str) -> List[NewsEntitySchema]:
        session_id = f"entity_{uuid.uuid4()}"
        text = f"HEADLINE: {headline}\nCONTENT: {content}"
        response = await self.gateway.chat(session_id, text, system_prompt_name="news_entity")
        try:
            clean_json = response.strip().strip("```json").strip("```").strip()
            data = json.loads(clean_json)
            return [NewsEntitySchema(**d) for d in data]
        except Exception as e:
            logger.error(f"Failed to parse entity JSON: {e}")
            return []


class EventEngine:
    def __init__(self):
        self.gateway = AIGatewayService()
        self._ensure_prompt()

    def _ensure_prompt(self):
        self.gateway.prompt_manager.register(
            PromptTemplate(
                name="news_event",
                template="""You are a strict JSON data extractor.
Detect financial events (Earnings Release, Dividend Announcement, Stock Split, Buyback, Acquisition, Merger, CEO Change, Product Launch, Litigation, Bankruptcy, Regulatory Investigation, Credit Rating Change, Macroeconomic Event).
Output MUST be valid JSON as an array of objects matching this schema:
[
  {
    "event_type": "string",
    "details": {"key": "value"}
  }
]
Do not include any markdown tags or other text.
""",
                variables=[]
            )
        )

    async def detect(self, headline: str, content: str) -> List[NewsEventSchema]:
        session_id = f"event_{uuid.uuid4()}"
        text = f"HEADLINE: {headline}\nCONTENT: {content}"
        response = await self.gateway.chat(session_id, text, system_prompt_name="news_event")
        try:
            clean_json = response.strip().strip("```json").strip("```").strip()
            data = json.loads(clean_json)
            return [NewsEventSchema(**d) for d in data]
        except Exception as e:
            logger.error(f"Failed to parse event JSON: {e}")
            return []
