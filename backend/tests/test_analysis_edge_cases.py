import pytest
from app.analysis.ratios import RatioEngine
from app.analysis.valuation import ValuationEngine
from app.analysis.forecasting import ForecastingEngine
from app.market_data.models import IncomeStatement, BalanceSheet, CashFlowStatement, StockQuote
from app.analysis.models import ForecastScenario, ForecastPoint

def get_base_statements():
    inc = IncomeStatement(
        date="2024", symbol="TEST", reported_currency="USD", cik="00", filling_date="2024",
        accepted_date="2024", calendar_year="2024", period="FY",
        revenue=1000, cost_of_revenue=400, gross_profit=600, gross_profit_ratio=0.6,
        research_and_development_expenses=100, general_and_administrative_expenses=50,
        selling_and_marketing_expenses=50, selling_general_and_administrative_expenses=100,
        other_expenses=0, operating_expenses=200, cost_and_expenses=600,
        interest_income=0, interest_expense=20, depreciation_and_amortization=20,
        ebitda=420, ebitdaratio=0.42, operating_income=400, operating_income_ratio=0.4,
        total_other_income_expenses_net=0, income_before_tax=380, income_before_tax_ratio=0.38,
        income_tax_expense=79.8, net_income=300.2, net_income_ratio=0.30,
        eps=3.0, epsdiluted=3.0, weighted_average_shs_out=100, weighted_average_shs_out_dil=100
    )
    bal = BalanceSheet(
        date="2024", symbol="TEST", reported_currency="USD", cik="00", filling_date="2024",
        accepted_date="2024", calendar_year="2024", period="FY",
        cash_and_cash_equivalents=200, short_term_investments=0, cash_and_short_term_investments=200,
        net_receivables=100, inventory=50, other_current_assets=0, total_current_assets=350,
        property_plant_equipment_net=500, goodwill=0, intangible_assets=0, long_term_investments=0,
        tax_assets=0, other_non_current_assets=0, total_non_current_assets=500, other_assets=0,
        total_assets=850, account_payables=50, short_term_debt=50, tax_payables=0, deferred_revenue=0,
        other_current_liabilities=0, total_current_liabilities=100, long_term_debt=150,
        deferred_revenue_non_current=0, deferred_tax_liabilities_non_current=0, other_non_current_liabilities=0,
        total_non_current_liabilities=150, other_liabilities=0, capital_lease_obligations=0,
        total_liabilities=250, preferred_stock=0, common_stock=100, retained_earnings=500,
        accumulated_other_comprehensive_income_loss=0, othertotal_stockholders_equity=0,
        total_stockholders_equity=600, total_equity=600, total_liabilities_and_stockholders_equity=850,
        minority_interest=0, total_liabilities_and_total_equity=850, total_investments=0,
        total_debt=200, net_debt=0
    )
    cf = CashFlowStatement(
        date="2024", symbol="TEST", reported_currency="USD", cik="00", filling_date="2024",
        accepted_date="2024", calendar_year="2024", period="FY",
        net_income=300.2, depreciation_and_amortization=20, deferred_income_tax=0,
        stock_based_compensation=0, change_in_working_capital=0, accounts_receivables=0,
        inventory=0, accounts_payables=0, other_working_capital=0, other_non_cash_items=0,
        net_cash_provided_by_operating_activities=320.2, investments_in_property_plant_and_equipment=0,
        acquisitions_net=0, purchases_of_investments=0, sales_maturities_of_investments=0,
        other_investing_activites=0, net_cash_used_for_investing_activites=0, debt_repayment=0,
        common_stock_issued=0, common_stock_repurchased=0, dividends_paid=0,
        other_financing_activites=0, net_cash_used_provided_by_financing_activities=0,
        effect_of_forex_changes_on_cash=0, net_change_in_cash=0, cash_at_end_of_period=0,
        cash_at_beginning_of_period=0, operating_cash_flow=320.2, free_cash_flow=300.2
    )
    quote = StockQuote(ticker="TEST", price=150.0, market_cap=15000.0)
    return inc, bal, cf, quote

def test_zero_revenue_and_zero_equity():
    inc, bal, cf, quote = get_base_statements()
    
    # Zero Revenue
    inc.revenue = 0.0
    # Zero Equity
    bal.total_equity = 0.0
    bal.total_stockholders_equity = 0.0
    
    engine = RatioEngine()
    ratios = engine.compute([inc], [bal], [cf], quote)
    
    assert ratios.gross_margin == 0.0
    assert ratios.operating_margin == 0.0
    assert ratios.net_margin == 0.0
    assert ratios.return_on_equity == 0.0
    assert ratios.debt_to_equity == 0.0
    
def test_zero_debt():
    inc, bal, cf, quote = get_base_statements()
    bal.total_debt = 0.0
    inc.interest_expense = 0.0
    
    val_engine = ValuationEngine()
    forecasts = ForecastScenario(scenario_name="Base", cagr_assumptions={}, projections=[
        ForecastPoint(year=2025, revenue=1100, eps=3.3, fcf=330.0, operating_margin=0.4)
    ])
    
    metrics = val_engine.compute([inc], [bal], [cf], quote, beta=1.0, forecasts=forecasts)
    
    assert metrics.cost_of_debt == 0.0
    assert metrics.wacc > 0.0
    assert metrics.dcf_intrinsic_value > 0.0

def test_negative_earnings_and_cashflow():
    inc, bal, cf, quote = get_base_statements()
    
    inc.net_income = -500.0
    inc.eps = -5.0
    cf.free_cash_flow = -300.0
    
    engine = RatioEngine()
    ratios = engine.compute([inc], [bal], [cf], quote)
    
    # PE ratio should fall back safely
    assert ratios.pe_ratio == 0.0
    
    forecast_engine = ForecastingEngine()
    # Need 4 years to calculate cagr, give it negative histories
    incs, cfs = [], []
    for _ in range(4):
        incs.append(inc)
        cfs.append(cf)
    
    forecasts = forecast_engine.compute(incs, cfs)
    # Default 5% CAGRs if impossible to compute
    assert forecasts.base_case.cagr_assumptions["fcf"] == 0.05 * 0.9

def test_missing_history_forecasting():
    inc, bal, cf, quote = get_base_statements()
    
    forecast_engine = ForecastingEngine()
    forecasts = forecast_engine.compute([inc], [cf]) # Only 1 year of data
    
    # Defaults to 5% cagr
    assert forecasts.base_case.projections[0].revenue > 1000.0
    assert forecasts.base_case.cagr_assumptions["revenue"] == 0.05 * 0.9

def test_valuation_engine_coverage():
    inc, bal, cf, quote = get_base_statements()
    val_engine = ValuationEngine()
    
    forecasts = ForecastScenario(scenario_name="Base", cagr_assumptions={}, projections=[
        ForecastPoint(year=2025, revenue=1100, eps=3.3, fcf=330.0, operating_margin=0.4)
    ])
    
    # 1. Hit line 56: WACC <= terminal_growth_rate
    # We can call dcf_valuation directly to force this
    intrinsic, ev = val_engine.dcf_valuation(
        base_case=forecasts,
        wacc=0.01,
        terminal_growth_rate=0.025,
        shares_outstanding=100,
        total_debt=0,
        cash=0
    )
    assert intrinsic > 0
    
    # 2. Hit lines 140-142: comparable_ev_ebitda block (pe is None)
    metrics = val_engine.compute(
        income_statements=[inc],
        balance_sheets=[bal],
        cash_flows=[cf],
        quote=quote,
        beta=1.0,
        forecasts=forecasts,
        comparable_pe_ratio=None,
        comparable_ev_ebitda=10.0
    )
    assert metrics.comparable_company_value is not None
    
    # 3. Hit lines 158-162: sensitivity missing or center row missing
    # We can pass an extremely low WACC causing sensitivity generation to fail or be empty
    metrics_empty = val_engine.compute(
        income_statements=[inc],
        balance_sheets=[bal],
        cash_flows=[cf],
        quote=quote,
        beta=0.0, # risk free rate is 0.04, so wacc will be positive but low. Wait, just mock it.
        forecasts=forecasts,
        risk_free_rate=-0.10, # Force WACC <= 0 to break sensitivity matrix
        market_return=0.09
    )
    # If WACC < 0, sensitivity drops those iterations, returning {}
    assert metrics_empty.fair_value_lower > 0
    assert metrics_empty.fair_value_upper > 0
