import pytest
from app.analysis.forecasting import ForecastingEngine
from app.market_data.models import IncomeStatement, CashFlowStatement

def test_forecasting_engine():
    engine = ForecastingEngine()
    
    incs = []
    cfs = []
    
    # 4 years: T=0, T-1, T-2, T-3 (Index 0 is newest)
    for i in range(4):
        # Revenue grew by ~10% each year looking forward, so looking backward it decreases
        rev = 1000 * (1.1 ** -i)
        eps = 5 * (1.1 ** -i)
        fcf = 100 * (1.1 ** -i)
        
        inc = IncomeStatement(
            date="2024", symbol="TEST", reported_currency="USD", cik="00", filling_date="2024",
            accepted_date="2024", calendar_year=str(2024-i), period="FY",
            revenue=rev, cost_of_revenue=400, gross_profit=500, gross_profit_ratio=0.5,
            research_and_development_expenses=100, general_and_administrative_expenses=50,
            selling_and_marketing_expenses=50, selling_general_and_administrative_expenses=100,
            other_expenses=0, operating_expenses=200, cost_and_expenses=600,
            interest_income=0, interest_expense=20, depreciation_and_amortization=20,
            ebitda=320, ebitdaratio=0.32, operating_income=300, operating_income_ratio=0.3,
            total_other_income_expenses_net=0, income_before_tax=280, income_before_tax_ratio=0.28,
            income_tax_expense=58.8, net_income=221.2, net_income_ratio=0.22,
            eps=eps, epsdiluted=eps, weighted_average_shs_out=100, weighted_average_shs_out_dil=100
        )
        cf = CashFlowStatement(
            date="2024", symbol="TEST", reported_currency="USD", cik="00", filling_date="2024",
            accepted_date="2024", calendar_year=str(2024-i), period="FY",
            net_income=221.2, depreciation_and_amortization=20, deferred_income_tax=0,
            stock_based_compensation=0, change_in_working_capital=0, accounts_receivables=0,
            inventory=0, accounts_payables=0, other_working_capital=0, other_non_cash_items=0,
            net_cash_provided_by_operating_activities=241.2, investments_in_property_plant_and_equipment=0,
            acquisitions_net=0, purchases_of_investments=0, sales_maturities_of_investments=0,
            other_investing_activites=0, net_cash_used_for_investing_activites=0, debt_repayment=0,
            common_stock_issued=0, common_stock_repurchased=0, dividends_paid=0,
            other_financing_activites=0, net_cash_used_provided_by_financing_activities=0,
            effect_of_forex_changes_on_cash=0, net_change_in_cash=0, cash_at_end_of_period=0,
            cash_at_beginning_of_period=0, operating_cash_flow=241.2, free_cash_flow=fcf
        )
        
        incs.append(inc)
        cfs.append(cf)
        
    forecasts = engine.compute(incs, cfs, forecast_years=5)
    
    assert forecasts.base_case.scenario_name == "Base"
    assert len(forecasts.base_case.projections) == 5
    
    # T=0 Revenue = 1000. Base growth should be ~9% (0.10 * 0.9 = 0.09)
    assert forecasts.base_case.projections[0].revenue > 1000
    assert forecasts.bull_case.projections[0].revenue > forecasts.base_case.projections[0].revenue
    assert forecasts.bear_case.projections[0].revenue < forecasts.base_case.projections[0].revenue
