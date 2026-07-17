from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.market_data.service import MarketDataService
from app.analysis.engine import AnalysisEngine
from app.models.portfolio import Portfolio as PortfolioModel, Holding as HoldingModel
from app.schemas.portfolio import (
    Portfolio, Holding, PortfolioAnalytics, PerformanceMetrics, AllocationMetrics, RiskMetrics
)
from app.portfolio.performance import PerformanceEngine
from app.portfolio.allocation import AllocationEngine
from app.portfolio.risk import PortfolioRiskEngine
from app.portfolio.benchmark import BenchmarkEngine
from app.core.exceptions import FinPilotException

class PortfolioEngine:
    def __init__(self, market_data_service: MarketDataService, analysis_engine: AnalysisEngine = None):
        self.md = market_data_service
        self.analysis = analysis_engine
        
        self.perf_engine = PerformanceEngine()
        self.alloc_engine = AllocationEngine()
        self.risk_engine = PortfolioRiskEngine()
        self.bench_engine = BenchmarkEngine()

    async def get_portfolio_analytics(self, db: AsyncSession, portfolio_id: int) -> PortfolioAnalytics:
        result = await db.execute(
            select(PortfolioModel)
            .options(selectinload(PortfolioModel.holdings))
            .filter(PortfolioModel.id == portfolio_id)
        )
        portfolio_db = result.scalars().first()
        
        if not portfolio_db:
            raise FinPilotException(status_code=404, message="Portfolio not found")
            
        hydrated_holdings = []
        profiles = {}
        total_value = 0.0
        
        for h_db in portfolio_db.holdings:
            quote = await self.md.get_quote(h_db.ticker_symbol)
            profile = await self.md.get_company_profile(h_db.ticker_symbol)
            
            if profile:
                profiles[h_db.ticker_symbol] = profile
                
            current_price = quote.price if quote else h_db.average_buy_price
            market_value = h_db.quantity * current_price
            unrealized_gl = market_value - h_db.cost_basis
            unrealized_gl_pct = (unrealized_gl / h_db.cost_basis) * 100.0 if h_db.cost_basis > 0 else 0.0
            
            total_value += market_value
            
            hydrated = Holding(
                id=h_db.id,
                portfolio_id=h_db.portfolio_id,
                ticker_symbol=h_db.ticker_symbol,
                asset_type=h_db.asset_type,
                quantity=h_db.quantity,
                average_buy_price=h_db.average_buy_price,
                cost_basis=h_db.cost_basis,
                realized_gain_loss=h_db.realized_gain_loss,
                current_price=current_price,
                market_value=market_value,
                unrealized_gain_loss=unrealized_gl,
                unrealized_gain_loss_pct=unrealized_gl_pct,
                sector=profile.sector if profile else "Unknown",
                industry=profile.industry if profile else "Unknown",
                country="Unknown",
                currency=profile.currency if profile else "USD"
            )
            hydrated_holdings.append(hydrated)
            
        for h in hydrated_holdings:
            h.weight = (h.market_value / total_value) * 100.0 if total_value > 0 else 0.0
            
        performance = self.perf_engine.compute(hydrated_holdings)
        allocation = self.alloc_engine.compute(hydrated_holdings, total_value)
        risk = self.risk_engine.compute(hydrated_holdings, profiles, total_value)
        
        return PortfolioAnalytics(
            performance=performance,
            allocation=allocation,
            risk=risk
        )

    async def get_user_portfolios_summary(self, user_id: int) -> dict:
        """
        Aggregate summary of all portfolios for a user.
        """
        # Placeholder logic for testing
        return {
            "total_value": 0.0,
            "daily_change_percent": 0.0,
            "portfolios_count": 0
        }
