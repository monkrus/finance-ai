from typing import List, Dict, Optional
from pydantic import BaseModel

class RatioMetrics(BaseModel):
    # Liquidity
    current_ratio: float
    quick_ratio: float
    cash_ratio: float
    
    # Profitability
    gross_margin: float
    operating_margin: float
    net_margin: float
    return_on_assets: float
    return_on_equity: float
    return_on_invested_capital: float
    
    # Leverage
    debt_to_equity: float
    debt_ratio: float
    interest_coverage: float
    
    # Efficiency
    asset_turnover: float
    inventory_turnover: float
    receivables_turnover: float
    
    # Valuation
    pe_ratio: float
    peg_ratio: Optional[float]
    ev_to_ebitda: float
    ev_to_sales: float
    price_to_book: float
    price_to_sales: float

    # Growth (CAGR)
    revenue_cagr_3y: Optional[float]
    eps_cagr_3y: Optional[float]
    fcf_cagr_3y: Optional[float]


class ValuationMetrics(BaseModel):
    dcf_intrinsic_value: float
    margin_of_safety: float
    wacc: float
    cost_of_equity: float
    cost_of_debt: float
    terminal_value: float
    ddm_intrinsic_value: Optional[float] = None
    enterprise_value: float
    fair_value_lower: float
    fair_value_upper: float
    comparable_company_value: Optional[float] = None
    sensitivity_matrix: Optional[Dict[str, Dict[str, float]]] = None

class RiskMetrics(BaseModel):
    beta: float
    volatility: float  # Annualized std dev
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    alpha: float
    correlation_to_market: float

class ScoreCategory(BaseModel):
    score: int  # 0 to 100
    explanation: str

class CompanyScores(BaseModel):
    health_score: ScoreCategory
    growth_score: ScoreCategory
    profitability_score: ScoreCategory
    value_score: ScoreCategory
    risk_score: ScoreCategory
    quality_score: ScoreCategory
    momentum_score: ScoreCategory
    overall_score: ScoreCategory

class ForecastPoint(BaseModel):
    year: int
    revenue: float
    eps: float
    fcf: float
    operating_margin: float

class ForecastScenario(BaseModel):
    scenario_name: str # Bull, Base, Bear
    cagr_assumptions: Dict[str, float]
    projections: List[ForecastPoint]

class ForecastingMetrics(BaseModel):
    bull_case: ForecastScenario
    base_case: ForecastScenario
    bear_case: ForecastScenario

class FinancialAnalysis(BaseModel):
    revenue: float
    revenue_growth: Optional[float]
    net_income: float
    gross_profit: float
    operating_income: float
    ebitda: float
    eps: float
    free_cash_flow: float
    operating_cash_flow: float
    capital_expenditure: float
    total_debt: float
    total_cash: float
    total_assets: float
    total_liabilities: float
    shareholders_equity: float
    book_value: float
    working_capital: float
    retained_earnings: float

class AnalysisReport(BaseModel):
    ticker: str
    company_name: str
    date_generated: str
    
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    risks: List[str]
    investment_thesis: str
    warning_signs: List[str]
    confidence_score: int # 0-100
    sources: List[str]
    
    financials: FinancialAnalysis
    ratios: RatioMetrics
    valuation: ValuationMetrics
    risk: RiskMetrics
    scores: CompanyScores
    forecasts: ForecastingMetrics
