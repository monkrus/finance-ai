import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.notifications.engine import NotificationEngine
from app.schemas.notification import NotificationCreate
from app.portfolio.engine import PortfolioEngine
from app.market_data.service import MarketDataService
from app.news.engine import NewsIntelligenceEngine

logger = logging.getLogger(__name__)

class AlertGenerator:
    """
    Background tasks that proactively query other modules and push alerts to the NotificationEngine.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.engine = NotificationEngine(db)

    async def run_portfolio_checks(self, user_id: int):
        """Generates alerts using Module 7 (Portfolio)"""
        try:
            port_engine = PortfolioEngine(market_data_service=MarketDataService())
            summary = await port_engine.get_user_portfolios_summary(self.db, user_id)
            
            # Example: Daily loss exceeds threshold
            if summary.get("daily_change_percent", 0.0) < -5.0:
                await self.engine.create_notification(NotificationCreate(
                    user_id=user_id,
                    title="Portfolio Alert: Heavy Daily Loss",
                    message=f"Your portfolio is down {summary['daily_change_percent']}% today.",
                    category="portfolio",
                    priority="high"
                ))
        except Exception as e:
            logger.error(f"Portfolio checks failed: {e}")

    async def run_market_checks(self, user_id: int, watchlist_tickers: list):
        """Generates alerts using Module 2 (Market Data)"""
        try:
            md_service = MarketDataService()
            for ticker in watchlist_tickers:
                quote = await md_service.get_quote(ticker)
                if quote and quote.change_percent and quote.change_percent > 5.0:
                    await self.engine.create_notification(NotificationCreate(
                        user_id=user_id,
                        title=f"Market Alert: {ticker} Spike",
                        message=f"{ticker} is up {quote.change_percent}% today.",
                        category="market",
                        priority="normal"
                    ))
        except Exception as e:
            logger.error(f"Market checks failed: {e}")

    async def run_news_checks(self, user_id: int):
        """Generates alerts using Module 8 (News Intelligence)"""
        try:
            news_engine = NewsIntelligenceEngine(self.db)
            breaking = await news_engine.get_recent_news(limit=1, article_type="Breaking")
            if breaking:
                await self.engine.create_notification(NotificationCreate(
                    user_id=user_id,
                    title=f"Breaking News: {breaking[0].headline}",
                    message="High impact news detected.",
                    category="news",
                    priority="high",
                    metadata_payload={"article_id": breaking[0].id}
                ))
        except Exception as e:
            logger.error(f"News checks failed: {e}")

    async def run_wealth_checks(self, user_id: int):
        """Generates alerts using Module 9 (Personal Finance)"""
        try:
            raise NotImplementedError("Wealth checks are not supported yet")
        except Exception as e:
            logger.error(f"Wealth checks failed: {e}")
