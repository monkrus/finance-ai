from typing import List
from datetime import datetime, timezone
import httpx
import xml.etree.ElementTree as ET
from app.news.providers.base import BaseNewsProvider
from app.schemas.news import NewsArticleCreate

class RSSAdapter(BaseNewsProvider):
    @property
    def provider_name(self) -> str:
        return "RSS"

    async def fetch_latest_news(self) -> List[NewsArticleCreate]:
        # Example Yahoo Finance RSS Feed for top news
        url = "https://finance.yahoo.com/news/rssindex"
        return await self._fetch_feed(url)

    async def fetch_company_news(self, ticker: str) -> List[NewsArticleCreate]:
        url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
        return await self._fetch_feed(url)

    async def _fetch_feed(self, url: str) -> List[NewsArticleCreate]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
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
                    # RFC 822 format typically
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
                    article_type="General"
                ))
        except Exception:
            pass
        return articles
