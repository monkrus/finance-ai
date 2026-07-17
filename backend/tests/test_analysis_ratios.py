import pytest
from app.analysis.ratios import RatioEngine
from app.market_data.models import IncomeStatement, BalanceSheet, CashFlowStatement, StockQuote

def test_ratio_engine_math():
    engine = RatioEngine()
    
    inc = IncomeStatement(
        date="2024-01-01", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024-01-01",
        accepted_date="2024-01-01", calendar_year="2023", period="FY",
        revenue=1000.0,
        cost_of_revenue=400.0,
        gross_profit=600.0,
        gross_profit_ratio=0.6,
        research_and_development_expenses=100.0,
        general_and_administrative_expenses=50.0,
        selling_and_marketing_expenses=50.0,
        selling_general_and_administrative_expenses=100.0,
        other_expenses=0.0,
        operating_expenses=200.0,
        cost_and_expenses=600.0,
        interest_income=10.0,
        interest_expense=20.0,
        depreciation_and_amortization=50.0,
        ebitda=450.0,
        ebitdaratio=0.45,
        operating_income=400.0,
        operating_income_ratio=0.4,
        total_other_income_expenses_net=-10.0,
        income_before_tax=390.0,
        income_before_tax_ratio=0.39,
        income_tax_expense=81.9, # 21%
        net_income=308.1,
        net_income_ratio=0.3081,
        eps=3.08,
        epsdiluted=3.08,
        weighted_average_shs_out=100.0,
        weighted_average_shs_out_dil=100.0
    )
    
    bal = BalanceSheet(
        date="2024-01-01", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024-01-01",
        accepted_date="2024-01-01", calendar_year="2023", period="FY",
        cash_and_cash_equivalents=200.0,
        short_term_investments=50.0,
        cash_and_short_term_investments=250.0,
        net_receivables=100.0,
        inventory=50.0,
        other_current_assets=50.0,
        total_current_assets=450.0,
        property_plant_equipment_net=500.0,
        goodwill=100.0,
        intangible_assets=50.0,
        long_term_investments=100.0,
        tax_assets=0.0,
        other_non_current_assets=0.0,
        total_non_current_assets=750.0,
        other_assets=0.0,
        total_assets=1200.0,
        account_payables=100.0,
        short_term_debt=50.0,
        tax_payables=20.0,
        deferred_revenue=30.0,
        other_current_liabilities=0.0,
        total_current_liabilities=200.0,
        long_term_debt=300.0,
        deferred_revenue_non_current=0.0,
        deferred_tax_liabilities_non_current=0.0,
        other_non_current_liabilities=0.0,
        total_non_current_liabilities=300.0,
        other_liabilities=0.0,
        capital_lease_obligations=0.0,
        total_liabilities=500.0,
        preferred_stock=0.0,
        common_stock=100.0,
        retained_earnings=600.0,
        accumulated_other_comprehensive_income_loss=0.0,
        othertotal_stockholders_equity=0.0,
        total_stockholders_equity=700.0,
        total_equity=700.0,
        total_liabilities_and_stockholders_equity=1200.0,
        minority_interest=0.0,
        total_liabilities_and_total_equity=1200.0,
        total_investments=150.0,
        total_debt=350.0,
        net_debt=150.0
    )
    
    cf = CashFlowStatement(
        date="2024-01-01", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024-01-01",
        accepted_date="2024-01-01", calendar_year="2023", period="FY",
        net_income=308.1,
        depreciation_and_amortization=50.0,
        deferred_income_tax=0.0,
        stock_based_compensation=20.0,
        change_in_working_capital=-10.0,
        accounts_receivables=-10.0,
        inventory=0.0,
        accounts_payables=0.0,
        other_working_capital=0.0,
        other_non_cash_items=0.0,
        net_cash_provided_by_operating_activities=368.1,
        investments_in_property_plant_and_equipment=-68.1,
        acquisitions_net=0.0,
        purchases_of_investments=0.0,
        sales_maturities_of_investments=0.0,
        other_investing_activites=0.0,
        net_cash_used_for_investing_activites=-68.1,
        debt_repayment=0.0,
        common_stock_issued=0.0,
        common_stock_repurchased=0.0,
        dividends_paid=-100.0,
        other_financing_activites=0.0,
        net_cash_used_provided_by_financing_activities=-100.0,
        effect_of_forex_changes_on_cash=0.0,
        net_change_in_cash=200.0,
        cash_at_end_of_period=200.0,
        cash_at_beginning_of_period=0.0,
        operating_cash_flow=368.1,
        free_cash_flow=300.0
    )
    
    quote = StockQuote(ticker="AAPL", price=50.0, market_cap=5000.0)
    
    ratios = engine.compute([inc], [bal], [cf], quote)
    
    # 450 CA / 200 CL
    assert ratios.current_ratio == 2.25
    # (450 - 50) / 200
    assert ratios.quick_ratio == 2.0
    # 200 / 200
    assert ratios.cash_ratio == 1.0
    
    assert round(ratios.gross_margin, 2) == 60.0
    assert round(ratios.operating_margin, 2) == 40.0
    assert round(ratios.net_margin, 2) == 30.81
    
    assert round(ratios.pe_ratio, 2) == 16.23
    assert ratios.price_to_book == 5000.0 / 700.0
