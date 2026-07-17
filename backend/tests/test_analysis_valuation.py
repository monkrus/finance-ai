import pytest
from app.analysis.valuation import ValuationEngine
from app.market_data.models import IncomeStatement, BalanceSheet, CashFlowStatement, StockQuote
from app.analysis.models import ForecastScenario, ForecastPoint

def test_valuation_engine_math():
    engine = ValuationEngine()
    
    # 5 years of FCF: 100, 110, 121, 133, 146
    forecasts = ForecastScenario(
        scenario_name="Base",
        cagr_assumptions={},
        projections=[
            ForecastPoint(year=2024, revenue=1000, eps=5, fcf=100, operating_margin=0.2),
            ForecastPoint(year=2025, revenue=1100, eps=5.5, fcf=110, operating_margin=0.2),
            ForecastPoint(year=2026, revenue=1210, eps=6.05, fcf=121, operating_margin=0.2),
            ForecastPoint(year=2027, revenue=1331, eps=6.65, fcf=133, operating_margin=0.2),
            ForecastPoint(year=2028, revenue=1464, eps=7.32, fcf=146, operating_margin=0.2)
        ]
    )
    
    inc = IncomeStatement(
        date="2023", symbol="TEST", reported_currency="USD", cik="00", filling_date="2023",
        accepted_date="2023", calendar_year="2023", period="FY",
        revenue=900, cost_of_revenue=400, gross_profit=500, gross_profit_ratio=0.55,
        research_and_development_expenses=100, general_and_administrative_expenses=50,
        selling_and_marketing_expenses=50, selling_general_and_administrative_expenses=100,
        other_expenses=0, operating_expenses=200, cost_and_expenses=600,
        interest_income=0, interest_expense=20, depreciation_and_amortization=20,
        ebitda=320, ebitdaratio=0.35, operating_income=300, operating_income_ratio=0.33,
        total_other_income_expenses_net=0, income_before_tax=280, income_before_tax_ratio=0.31,
        income_tax_expense=58.8, net_income=221.2, net_income_ratio=0.24,
        eps=2.21, epsdiluted=2.21, weighted_average_shs_out=100, weighted_average_shs_out_dil=100
    )
    bal = BalanceSheet(
        date="2023", symbol="TEST", reported_currency="USD", cik="00", filling_date="2023",
        accepted_date="2023", calendar_year="2023", period="FY",
        cash_and_cash_equivalents=50, short_term_investments=0, cash_and_short_term_investments=50,
        net_receivables=100, inventory=50, other_current_assets=0, total_current_assets=200,
        property_plant_equipment_net=500, goodwill=0, intangible_assets=0, long_term_investments=0,
        tax_assets=0, other_non_current_assets=0, total_non_current_assets=500, other_assets=0,
        total_assets=700, account_payables=50, short_term_debt=50, tax_payables=0, deferred_revenue=0,
        other_current_liabilities=0, total_current_liabilities=100, long_term_debt=150,
        deferred_revenue_non_current=0, deferred_tax_liabilities_non_current=0, other_non_current_liabilities=0,
        total_non_current_liabilities=150, other_liabilities=0, capital_lease_obligations=0,
        total_liabilities=250, preferred_stock=0, common_stock=100, retained_earnings=350,
        accumulated_other_comprehensive_income_loss=0, othertotal_stockholders_equity=0,
        total_stockholders_equity=450, total_equity=450, total_liabilities_and_stockholders_equity=700,
        minority_interest=0, total_liabilities_and_total_equity=700, total_investments=0,
        total_debt=200, net_debt=150
    )
    quote = StockQuote(ticker="TEST", price=30.0, market_cap=3000.0)
    
    val = engine.compute(
        income_statements=[inc],
        balance_sheets=[bal],
        cash_flows=[],
        quote=quote,
        beta=1.0,
        forecasts=forecasts,
        risk_free_rate=0.04,
        market_return=0.09
    )
    
    # Cost of equity = 0.04 + 1.0 * (0.09 - 0.04) = 0.09
    assert val.cost_of_equity == 0.09
    # Cost of debt = 20 / 200 = 0.1
    assert val.cost_of_debt == 0.1
    # WACC = (3000/3200)*0.09 + (200/3200)*0.1*(1 - 0.21)
    # WACC = 0.9375 * 0.09 + 0.0625 * 0.079 = 0.084375 + 0.0049375 = 0.0893125
    assert round(val.wacc, 5) == round(0.0893125, 5)
    
    assert val.dcf_intrinsic_value > 0
    assert val.enterprise_value > 0
