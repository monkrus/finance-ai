from typing import List
from datetime import datetime, timezone
import httpx
import xml.etree.ElementTree as ET
from app.news.providers.base import BaseNewsProvider
from app.schemas.news import NewsArticleCreate

class SECPressReleaseAdapter(BaseNewsProvider):
    @property
    def provider_name(self) -> str:
        return "SEC"

    async def fetch_latest_news(self) -> List[NewsArticleCreate]:
        # SEC provides RSS feeds for press releases
        url = "https://www.sec.gov/news/pressreleases.rss"
        return await self._fetch_sec_feed(url)

    async def fetch_company_news(self, ticker: str) -> List[NewsArticleCreate]:
        # CIK would be needed for true SEC API, but SEC doesn't have a simple 
        # ticker-based RSS for news. Fallback to empty list or search endpoint if available.
        return []

    async def _fetch_sec_feed(self, url: str) -> List[NewsArticleCreate]:
        try:
            async with httpx.AsyncClient() as client:
                # SEC requires a user agent with contact info
                headers = {"User-Agent": "FinPilot AI/1.0 (contact@finpilot.ai)"}
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                return self._parse_rss(response.text)
        except Exception:
            return []
            
    def _parse_rss(self, xml_content: str) -> List[NewsArticleCreate]:
        articles = []
        try:
            root = ET.fromstring(xml_content)
            channel = root.find("channel")
            if channel is None:
                return articles
                
            for item in channel.findall("item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                description = item.findtext("description", "")
                pub_date_str = item.findtext("pubDate", "")
                
                try:
                    from email.utils import parsedate_to_datetime
                    pub_date = parsedate_to_datetime(pub_date_str)
                except Exception:
                    pub_date = datetime.now(timezone.utc)
                    
                articles.append(NewsArticleCreate(
                    provider=self.provider_name,
                    provider_id=link,
                    headline=title,
                    content=description,
                    source_url=link,
                    image_url=None,
                    published_at=pub_date,
                    article_type="Regulatory"
                ))
        except Exception:
            pass
        return articles
