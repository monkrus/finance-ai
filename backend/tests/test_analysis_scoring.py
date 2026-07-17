import pytest
from app.analysis.scoring import CompanyScoringEngine
from app.analysis.models import RatioMetrics, RiskMetrics

def test_company_scoring():
    engine = CompanyScoringEngine()
    
    ratios = RatioMetrics(
        current_ratio=2.0, quick_ratio=1.5, cash_ratio=1.0,
        gross_margin=50.0, operating_margin=20.0, net_margin=15.0,
        return_on_assets=10.0, return_on_equity=20.0, return_on_invested_capital=15.0,
        debt_to_equity=0.2, debt_ratio=0.1, interest_coverage=10.0,
        asset_turnover=1.0, inventory_turnover=5.0, receivables_turnover=5.0,
        pe_ratio=10.0, peg_ratio=0.5, ev_to_ebitda=8.0, ev_to_sales=2.0,
        price_to_book=2.0, price_to_sales=2.0,
        revenue_cagr_3y=0.2, eps_cagr_3y=0.2, fcf_cagr_3y=0.2
    )
    
    risk = RiskMetrics(
        beta=1.0, volatility=0.2, sharpe_ratio=1.5, sortino_ratio=2.0,
        max_drawdown=0.1, alpha=0.05, correlation_to_market=0.8
    )
    
    scores = engine.compute(ratios, risk)
    
    assert scores.health_score.score > 50
    assert scores.profitability_score.score > 50
    assert scores.growth_score.score > 50
    assert scores.value_score.score > 50
    assert scores.risk_score.score > 50
    assert scores.overall_score.score > 50

def test_company_scoring_weak():
    engine = CompanyScoringEngine()
    
    ratios = RatioMetrics(
        current_ratio=0.5, quick_ratio=0.5, cash_ratio=0.5,
        gross_margin=10.0, operating_margin=2.0, net_margin=1.0,
        return_on_assets=2.0, return_on_equity=5.0, return_on_invested_capital=2.0,
        debt_to_equity=3.0, debt_ratio=0.8, interest_coverage=2.0,
        asset_turnover=0.5, inventory_turnover=1.0, receivables_turnover=1.0,
        pe_ratio=40.0, peg_ratio=3.0, ev_to_ebitda=20.0, ev_to_sales=10.0,
        price_to_book=10.0, price_to_sales=10.0,
        revenue_cagr_3y=0.02, eps_cagr_3y=-0.05, fcf_cagr_3y=0.0
    )
    
    risk = RiskMetrics(
        beta=1.5, volatility=0.5, sharpe_ratio=0.5, sortino_ratio=0.5,
        max_drawdown=0.6, alpha=-0.1, correlation_to_market=0.8
    )
    
    scores = engine.compute(ratios, risk)
    
    assert scores.health_score.score < 50
    assert scores.profitability_score.score < 50
    assert scores.growth_score.score < 50
    assert scores.value_score.score < 50
    assert scores.risk_score.score < 50
    assert scores.overall_score.score < 50
