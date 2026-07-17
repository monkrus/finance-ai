from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import date

class CompanyProfile(BaseModel):
    ticker: str
    company_name: str
    currency: Optional[str] = None
    exchange: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    ceo: Optional[str] = None
    market_cap: Optional[float] = None
    beta: Optional[float] = None
    price: Optional[float] = None
    image: Optional[str] = None
    is_actively_trading: Optional[bool] = None

class StockQuote(BaseModel):
    ticker: str
    price: float
    change: Optional[float] = None
    change_percent: Optional[float] = None
    day_low: Optional[float] = None
    day_high: Optional[float] = None
    year_low: Optional[float] = None
    year_high: Optional[float] = None
    market_cap: Optional[float] = None
    volume: Optional[int] = None
    avg_volume: Optional[int] = None
    exchange: Optional[str] = None
    timestamp: Optional[int] = None

class HistoricalPrice(BaseModel):
    date: str # YYYY-MM-DD
    open: float
    high: float
    low: float
    close: float
    adj_close: Optional[float] = None
    volume: int
    unadjusted_volume: Optional[int] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    vwap: Optional[float] = None

class HistoricalPriceSeries(BaseModel):
    ticker: str
    prices: List[HistoricalPrice]

class FinancialStatementBase(BaseModel):
    date: str # YYYY-MM-DD
    symbol: str
    reported_currency: str
    cik: str
    filling_date: str
    accepted_date: str
    calendar_year: str
    period: str # FY or Q1, Q2, etc.

class IncomeStatement(FinancialStatementBase):
    revenue: float
    cost_of_revenue: float
    gross_profit: float
    gross_profit_ratio: float
    research_and_development_expenses: float
    general_and_administrative_expenses: float
    selling_and_marketing_expenses: float
    selling_general_and_administrative_expenses: float
    other_expenses: float
    operating_expenses: float
    cost_and_expenses: float
    interest_income: float
    interest_expense: float
    depreciation_and_amortization: float
    ebitda: float
    ebitdaratio: float
    operating_income: float
    operating_income_ratio: float
    total_other_income_expenses_net: float
    income_before_tax: float
    income_before_tax_ratio: float
    income_tax_expense: float
    net_income: float
    net_income_ratio: float
    eps: float
    epsdiluted: float
    weighted_average_shs_out: float
    weighted_average_shs_out_dil: float

class BalanceSheet(FinancialStatementBase):
    cash_and_cash_equivalents: float
    short_term_investments: float
    cash_and_short_term_investments: float
    net_receivables: float
    inventory: float
    other_current_assets: float
    total_current_assets: float
    property_plant_equipment_net: float
    goodwill: float
    intangible_assets: float
    long_term_investments: float
    tax_assets: float
    other_non_current_assets: float
    total_non_current_assets: float
    other_assets: float
    total_assets: float
    account_payables: float
    short_term_debt: float
    tax_payables: float
    deferred_revenue: float
    other_current_liabilities: float
    total_current_liabilities: float
    long_term_debt: float
    deferred_revenue_non_current: float
    deferred_tax_liabilities_non_current: float
    other_non_current_liabilities: float
    total_non_current_liabilities: float
    other_liabilities: float
    capital_lease_obligations: float
    total_liabilities: float
    preferred_stock: float
    common_stock: float
    retained_earnings: float
    accumulated_other_comprehensive_income_loss: float
    othertotal_stockholders_equity: float
    total_stockholders_equity: float
    total_equity: float
    total_liabilities_and_stockholders_equity: float
    minority_interest: float
    total_liabilities_and_total_equity: float
    total_investments: float
    total_debt: float
    net_debt: float

class CashFlowStatement(FinancialStatementBase):
    net_income: float
    depreciation_and_amortization: float
    deferred_income_tax: float
    stock_based_compensation: float
    change_in_working_capital: float
    accounts_receivables: float
    inventory: float
    accounts_payables: float
    other_working_capital: float
    other_non_cash_items: float
    net_cash_provided_by_operating_activities: float
    investments_in_property_plant_and_equipment: float
    acquisitions_net: float
    purchases_of_investments: float
    sales_maturities_of_investments: float
    other_investing_activites: float
    net_cash_used_for_investing_activites: float
    debt_repayment: float
    common_stock_issued: float
    common_stock_repurchased: float
    dividends_paid: float
    other_financing_activites: float
    net_cash_used_provided_by_financing_activities: float
    effect_of_forex_changes_on_cash: float
    net_change_in_cash: float
    cash_at_end_of_period: float
    cash_at_beginning_of_period: float
    operating_cash_flow: float
    free_cash_flow: float

class CompanySearchResult(BaseModel):
    ticker: str
    name: Optional[str] = None
    exchange: Optional[str] = None

class FinancialRatios(BaseModel):
    symbol: str
    date: str
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    return_on_equity: Optional[float] = None

class MarketNews(BaseModel):
    id: str
    symbol: str
    title: str
    published_at: str
    source: str
    url: str
    summary: Optional[str] = None

class EconomicIndicator(BaseModel):
    indicator_id: str
    name: str
    date: str
    value: float

class ExchangeRate(BaseModel):
    base_currency: str
    target_currency: str
    rate: float
    timestamp: str

class EarningsEvent(BaseModel):
    symbol: str
    date: str
    eps_estimate: Optional[float] = None
    eps_actual: Optional[float] = None
    revenue_estimate: Optional[float] = None
    revenue_actual: Optional[float] = None

class DividendHistory(BaseModel):
    symbol: str
    date: str
    amount: float
    declaration_date: Optional[str] = None
    record_date: Optional[str] = None
    payment_date: Optional[str] = None

class StockSplit(BaseModel):
    symbol: str
    date: str
    numerator: float
    denominator: float

class MarketIndex(BaseModel):
    symbol: str
    name: str
    price: float
    change: Optional[float] = None
    change_percent: Optional[float] = None

class SectorIndustryClass(BaseModel):
    symbol: str
    sector: str
    industry: str
