import datetime
from typing import List

from app.market_data.service import MarketDataService
from app.analysis.models import (
    AnalysisReport, FinancialAnalysis, RatioMetrics, 
    ValuationMetrics, RiskMetrics, ForecastingMetrics, CompanyScores
)
from app.analysis.ratios import RatioEngine
from app.analysis.valuation import ValuationEngine
from app.analysis.risk import RiskEngine
from app.analysis.forecasting import ForecastingEngine
from app.analysis.scoring import CompanyScoringEngine

class AnalysisEngine:
    """
    Facade orchestrating all financial calculations.
    Consumes MarketDataService exclusively.
    """
    def __init__(self, market_data_service: MarketDataService):
        self.md = market_data_service
        self.ratio_engine = RatioEngine()
        self.valuation_engine = ValuationEngine()
        self.risk_engine = RiskEngine()
        self.forecasting_engine = ForecastingEngine()
        self.scoring_engine = CompanyScoringEngine()

    async def generate_full_report(self, ticker: str) -> AnalysisReport:
        # 1. Fetch raw data concurrently (or sequentially for simplicity here)
        profile = await self.md.get_company_profile(ticker)
        if not profile:
            raise ValueError(f"Company profile not found for {ticker}")
            
        quote = await self.md.get_quote(ticker)
        income_statements = await self.md.get_income_statements(ticker, limit=4)
        balance_sheets = await self.md.get_balance_sheets(ticker, limit=4)
        cash_flows = await self.md.get_cash_flow_statements(ticker, limit=4)
        
        if not (income_statements and balance_sheets and cash_flows and quote):
            raise ValueError(f"Insufficient financial statements or quote for {ticker}")
            
        # For Risk Engine, need 1 year history
        asset_history = await self.md.get_historical_prices(ticker)
        market_history = await self.md.get_historical_prices("SPY") # Proxy for market
        
        # 2. Ratios
        ratios = self.ratio_engine.compute(income_statements, balance_sheets, cash_flows, quote)
        
        # 3. Risk
        if asset_history and market_history:
            risk = self.risk_engine.compute(asset_history, market_history)
        else:
            # Fallback if no history
            risk = RiskMetrics(beta=1.0, volatility=0.2, sharpe_ratio=1.0, sortino_ratio=1.0, max_drawdown=0.2, alpha=0.0, correlation_to_market=1.0)
            if profile.beta: risk.beta = profile.beta
            
        # 4. Forecasts
        forecasts = self.forecasting_engine.compute(income_statements, cash_flows)
        
        # 5. Valuation
        div_history = await self.md.get_dividend_history(ticker)
        current_dividend = 0.0
        dividend_growth_rate = 0.02
        if div_history and len(div_history) > 0:
            current_dividend = div_history[0].amount
            if len(div_history) > 1 and div_history[1].amount > 0:
                dividend_growth_rate = (div_history[0].amount - div_history[1].amount) / div_history[1].amount
                dividend_growth_rate = max(-1.0, min(0.15, dividend_growth_rate)) # Clamp
        
        valuation = self.valuation_engine.compute(
            income_statements=income_statements,
            balance_sheets=balance_sheets,
            cash_flows=cash_flows,
            quote=quote,
            beta=risk.beta,
            forecasts=forecasts.base_case,
            current_dividend=current_dividend,
            dividend_growth_rate=dividend_growth_rate,
            comparable_pe_ratio=15.0, # Sector median placeholder
            comparable_ev_ebitda=10.0 # Sector median placeholder
        )
        
        # 6. Scoring
        scores = self.scoring_engine.compute(ratios, risk)
        
        # 7. Financial Analysis Basics
        inc = income_statements[0]
        bal = balance_sheets[0]
        cf = cash_flows[0]
        
        rev_growth = None
        if len(income_statements) > 1 and income_statements[1].revenue > 0:
            rev_growth = (inc.revenue - income_statements[1].revenue) / income_statements[1].revenue
            
        basics = FinancialAnalysis(
            revenue=inc.revenue,
            revenue_growth=rev_growth,
            net_income=inc.net_income,
            gross_profit=inc.gross_profit,
            operating_income=inc.operating_income,
            ebitda=inc.ebitda,
            eps=inc.eps,
            free_cash_flow=cf.free_cash_flow,
            operating_cash_flow=cf.operating_cash_flow,
            capital_expenditure=cf.investments_in_property_plant_and_equipment,
            total_debt=bal.total_debt,
            total_cash=bal.cash_and_cash_equivalents,
            total_assets=bal.total_assets,
            total_liabilities=bal.total_liabilities,
            shareholders_equity=bal.total_stockholders_equity,
            book_value=bal.total_stockholders_equity, # Simplified
            working_capital=bal.total_current_assets - bal.total_current_liabilities,
            retained_earnings=bal.retained_earnings
        )
        
        # Synthesis logic (Simplified)
        thesis = "Strong fundamental outlook." if scores.overall_score.score >= 70 else "Weak fundamental outlook requiring caution."
        
        return AnalysisReport(
            ticker=ticker.upper(),
            company_name=profile.company_name,
            date_generated=datetime.datetime.now().isoformat(),
            summary=f"Automated quantitative analysis for {profile.company_name}.",
            strengths=[scores.health_score.explanation, scores.profitability_score.explanation],
            weaknesses=[scores.risk_score.explanation],
            risks=["Macroeconomic volatility", "Sector rotation"],
            investment_thesis=thesis,
            warning_signs=[],
            confidence_score=scores.overall_score.score,
            sources=["FinPilot Market Data Layer"],
            financials=basics,
            ratios=ratios,
            valuation=valuation,
            risk=risk,
            scores=scores,
            forecasts=forecasts
        )
