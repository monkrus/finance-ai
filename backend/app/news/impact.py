import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.portfolio import Portfolio, Holding
from app.schemas.news import PortfolioImpactSchema, NewsEntitySchema, NewsEventSchema

logger = logging.getLogger(__name__)

class PortfolioImpactEngine:
    """
    Correlates extracted news entities and events with a user's portfolio holdings
    to determine the impact of a news article on a portfolio.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def determine_impact(self, user_id: int, entities: List[NewsEntitySchema], events: List[NewsEventSchema], sentiment_score: float, importance_score: int = 0) -> List[PortfolioImpactSchema]:
        # Fetch all portfolios for the user
        result = await self.db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
        portfolios = result.scalars().all()
        
        impacts = []
        tickers_in_news = [e.entity_name.upper() for e in entities if e.entity_type.lower() == "ticker"]
        
        for p in portfolios:
            # Load holdings
            hold_res = await self.db.execute(select(Holding).where(Holding.portfolio_id == p.id))
            holdings = hold_res.scalars().all()
            
            total_portfolio_cost = sum([h.cost_basis for h in holdings])
            
            affected = []
            affected_exposure = 0.0
            for h in holdings:
                if h.ticker_symbol.upper() in tickers_in_news:
                    affected.append(h.ticker_symbol)
                    if total_portfolio_cost > 0:
                        affected_exposure += (h.cost_basis / total_portfolio_cost)
            
            if affected:
                # Calculate Alert Priority
                # CRITICAL: Importance Score > 80 AND User Portfolio Exposure > 10%
                # HIGH: Importance Score > 60 AND User Portfolio Exposure > 5%
                # MEDIUM: Importance Score > 40 AND User Portfolio Exposure > 0%
                # LOW: All other matches.
                
                exposure_pct = affected_exposure * 100
                priority = "LOW"
                
                if importance_score > 80 and exposure_pct > 10.0:
                    priority = "CRITICAL"
                elif importance_score > 60 and exposure_pct > 5.0:
                    priority = "HIGH"
                elif importance_score > 40 and exposure_pct > 0.0:
                    priority = "MEDIUM"
                elif exposure_pct > 0:
                    priority = "LOW"
                    
                impacts.append(
                    PortfolioImpactSchema(
                        portfolio_id=p.id,
                        affected_holdings=affected,
                        impact_score=sentiment_score,
                        impact_reasoning=f"News impacts {', '.join(affected)} (Exposure: {exposure_pct:.1f}%).",
                        alert_priority=priority
                    )
                )
                
        return impacts
