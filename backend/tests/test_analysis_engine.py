import pytest
from unittest.mock import AsyncMock
from app.analysis.engine import AnalysisEngine
from app.market_data.service import MarketDataService
from app.market_data.models import (
    CompanyProfile, StockQuote, HistoricalPriceSeries,
    IncomeStatement, BalanceSheet, CashFlowStatement, HistoricalPrice
)

@pytest.mark.asyncio
async def test_analysis_engine():
    mock_md = AsyncMock(spec=MarketDataService)
    
    mock_md.get_company_profile.return_value = CompanyProfile(
        ticker="AAPL", company_name="Apple Inc.", beta=1.2
    )
    mock_md.get_quote.return_value = StockQuote(
        ticker="AAPL", price=150.0, market_cap=2.5e12
    )
    
    inc = IncomeStatement(
        date="2024", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024",
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
        date="2024", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024",
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
        date="2024", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024",
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
    
    mock_md.get_income_statements.return_value = [inc] * 4
    mock_md.get_balance_sheets.return_value = [bal] * 4
    mock_md.get_cash_flow_statements.return_value = [cf] * 4
    
    hist_prices = HistoricalPriceSeries(
        ticker="AAPL",
        prices=[HistoricalPrice(date="1", open=150, high=150, low=150, close=150, volume=100)] * 10
    )
    mock_md.get_historical_prices.return_value = hist_prices
    
    engine = AnalysisEngine(market_data_service=mock_md)
    report = await engine.generate_full_report("AAPL")
    
    assert report.ticker == "AAPL"
    assert report.company_name == "Apple Inc."
    assert report.financials.revenue == 1000
    assert report.ratios.current_ratio == 3.5
    assert report.risk.beta > 0
    assert report.scores.overall_score.score > 0
    assert report.valuation.wacc > 0

@pytest.mark.asyncio
async def test_analysis_engine_edge_cases():
    mock_md = AsyncMock(spec=MarketDataService)
    engine = AnalysisEngine(market_data_service=mock_md)
    
    # Missing profile
    mock_md.get_company_profile.return_value = None
    with pytest.raises(ValueError, match="Company profile not found"):
        await engine.generate_full_report("AAPL")
        
    mock_md.get_company_profile.return_value = CompanyProfile(ticker="AAPL", company_name="Apple Inc.")
    # Missing financials
    mock_md.get_quote.return_value = None
    with pytest.raises(ValueError, match="Insufficient financial statements"):
        await engine.generate_full_report("AAPL")
        
    mock_md.get_quote.return_value = StockQuote(ticker="AAPL", price=150.0, market_cap=2.5e12)
    inc = IncomeStatement(
        date="2024", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024",
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
        date="2024", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024",
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
        date="2024", symbol="AAPL", reported_currency="USD", cik="00", filling_date="2024",
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
    mock_md.get_income_statements.return_value = [inc] * 4
    mock_md.get_balance_sheets.return_value = [bal] * 4
    mock_md.get_cash_flow_statements.return_value = [cf] * 4
    
    # Missing historical price series
    mock_md.get_historical_prices.return_value = None
    
    report = await engine.generate_full_report("AAPL")
    assert report.risk.beta == 1.0 # Uses fallback

