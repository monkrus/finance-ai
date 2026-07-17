import pytest
import yfinance as yf
from unittest.mock import AsyncMock
from app.analysis.engine import AnalysisEngine
from app.market_data.service import MarketDataService
from app.market_data.models import (
    CompanyProfile, StockQuote, HistoricalPriceSeries,
    IncomeStatement, BalanceSheet, CashFlowStatement, HistoricalPrice, DividendHistory
)

# Test real companies
TICKERS = ["AAPL", "MSFT", "NVDA", "RELIANCE.NS", "TCS.NS"]

def fetch_yfinance_data(ticker_symbol: str):
    ticker = yf.Ticker(ticker_symbol)
    
    # Get basic info
    info = ticker.info
    hist = ticker.history(period="1y")
    financials = ticker.financials.transpose() if not ticker.financials.empty else None
    balance_sheet = ticker.balance_sheet.transpose() if not ticker.balance_sheet.empty else None
    cashflow = ticker.cashflow.transpose() if not ticker.cashflow.empty else None
    dividends = ticker.dividends
    
    return {
        "info": info,
        "hist": hist,
        "financials": financials,
        "balance_sheet": balance_sheet,
        "cashflow": cashflow,
        "dividends": dividends
    }

def safe_get(df, index, col, default=0.0):
    try:
        val = df.iloc[index][col]
        return float(val) if not type(val).__name__ == "NAType" and val == val else default
    except Exception:
        return default

@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", TICKERS)
async def test_real_world_valuation(ticker):
    # Fetch real data
    data = fetch_yfinance_data(ticker)
    
    info = data["info"]
    financials = data["financials"]
    bs = data["balance_sheet"]
    cf = data["cashflow"]
    hist = data["hist"]
    
    if financials is None or bs is None or cf is None or len(financials) < 2:
        pytest.skip(f"Not enough financial data for {ticker} from Yahoo Finance.")
        
    mock_md = AsyncMock(spec=MarketDataService)
    
    # 1. Profile
    import math
    raw_beta = info.get("beta")
    try:
        beta = float(raw_beta)
        if math.isnan(beta):
            beta = 1.0
    except (TypeError, ValueError):
        beta = 1.0

    mock_md.get_company_profile.return_value = CompanyProfile(
        ticker=ticker,
        company_name=info.get("shortName", ticker),
        beta=beta
    )
    
    # 2. Quote
    price = info.get("currentPrice") or info.get("regularMarketPrice") or 10.0
    
    raw_shares = info.get("sharesOutstanding")
    try:
        shares = float(raw_shares)
        if math.isnan(shares):
            shares = 1000000.0
    except (TypeError, ValueError):
        shares = 1000000.0
        
    raw_mcap = info.get("marketCap")
    try:
        mcap = float(raw_mcap)
        if math.isnan(mcap):
            mcap = float(price) * shares
    except (TypeError, ValueError):
        mcap = float(price) * shares

    mock_md.get_quote.return_value = StockQuote(
        ticker=ticker, price=float(price), market_cap=mcap
    )
    
    # 3. Income Statements
    incs = []
    limit = min(4, len(financials), len(bs), len(cf))
    for i in range(limit):
        rev = safe_get(financials, i, "Total Revenue")
        ni = safe_get(financials, i, "Net Income")
        # Use the parsed shares from above
        inc = IncomeStatement(
            date=str(financials.index[i]), symbol=ticker, reported_currency="USD", cik="00", filling_date="", accepted_date="",
            calendar_year=str(financials.index[i].year), period="FY",
            revenue=rev,
            cost_of_revenue=safe_get(financials, i, "Cost Of Revenue"),
            gross_profit=safe_get(financials, i, "Gross Profit"),
            gross_profit_ratio=safe_get(financials, i, "Gross Profit") / rev if rev else 0.0,
            research_and_development_expenses=safe_get(financials, i, "Research And Development"),
            general_and_administrative_expenses=safe_get(financials, i, "General And Administrative Expense"),
            selling_and_marketing_expenses=0.0, selling_general_and_administrative_expenses=0.0, other_expenses=0.0,
            operating_expenses=safe_get(financials, i, "Operating Expense"),
            cost_and_expenses=0.0,
            interest_income=0.0,
            interest_expense=safe_get(financials, i, "Interest Expense"),
            depreciation_and_amortization=0.0,
            ebitda=safe_get(financials, i, "EBITDA"),
            ebitdaratio=safe_get(financials, i, "EBITDA") / rev if rev else 0.0,
            operating_income=safe_get(financials, i, "Operating Income"),
            operating_income_ratio=safe_get(financials, i, "Operating Income") / rev if rev else 0.0,
            total_other_income_expenses_net=0.0,
            income_before_tax=safe_get(financials, i, "Pretax Income"),
            income_before_tax_ratio=safe_get(financials, i, "Pretax Income") / rev if rev else 0.0,
            income_tax_expense=safe_get(financials, i, "Tax Provision"),
            net_income=ni,
            net_income_ratio=ni / rev if rev else 0.0,
            eps=ni / shares if shares else 0,
            epsdiluted=ni / shares if shares else 0,
            weighted_average_shs_out=shares,
            weighted_average_shs_out_dil=shares
        )
        incs.append(inc)
    
    # 4. Balance Sheets
    bals = []
    for i in range(limit):
        bal = BalanceSheet(
            date=str(bs.index[i]), symbol=ticker, reported_currency="USD", cik="00", filling_date="", accepted_date="",
            calendar_year=str(bs.index[i].year), period="FY",
            cash_and_cash_equivalents=safe_get(bs, i, "Cash And Cash Equivalents"), short_term_investments=0.0,
            cash_and_short_term_investments=safe_get(bs, i, "Cash And Cash Equivalents"), net_receivables=safe_get(bs, i, "Net Receivables", 0),
            inventory=safe_get(bs, i, "Inventory", 0), other_current_assets=0.0,
            total_current_assets=safe_get(bs, i, "Current Assets", 0), property_plant_equipment_net=0.0,
            goodwill=0.0, intangible_assets=0.0, long_term_investments=0.0, tax_assets=0.0, other_non_current_assets=0.0,
            total_non_current_assets=0.0, other_assets=0.0, total_assets=safe_get(bs, i, "Total Assets", 100),
            account_payables=0.0, short_term_debt=0.0, tax_payables=0.0, deferred_revenue=0.0,
            other_current_liabilities=0.0, total_current_liabilities=safe_get(bs, i, "Current Liabilities", 0),
            long_term_debt=safe_get(bs, i, "Long Term Debt", 0), deferred_revenue_non_current=0.0, deferred_tax_liabilities_non_current=0.0,
            other_non_current_liabilities=0.0, total_non_current_liabilities=0.0, other_liabilities=0.0, capital_lease_obligations=0.0,
            total_liabilities=safe_get(bs, i, "Total Liabilities Net Minority Interest", 50), preferred_stock=0.0, common_stock=0.0, retained_earnings=0.0,
            accumulated_other_comprehensive_income_loss=0.0, othertotal_stockholders_equity=0.0,
            total_stockholders_equity=safe_get(bs, i, "Stockholders Equity", 50), total_equity=safe_get(bs, i, "Stockholders Equity", 50),
            total_liabilities_and_stockholders_equity=safe_get(bs, i, "Total Assets", 100), minority_interest=0.0,
            total_liabilities_and_total_equity=safe_get(bs, i, "Total Assets", 100), total_investments=0.0,
            total_debt=safe_get(bs, i, "Total Debt", 0), net_debt=safe_get(bs, i, "Net Debt", 0)
        )
        bals.append(bal)

    # 5. Cash Flows
    cfs = []
    for i in range(limit):
        fcf = safe_get(cf, i, "Free Cash Flow")
        ocf = safe_get(cf, i, "Operating Cash Flow")
        cf_obj = CashFlowStatement(
            date=str(cf.index[i]), symbol=ticker, reported_currency="USD", cik="00", filling_date="", accepted_date="",
            calendar_year=str(cf.index[i].year), period="FY",
            net_income=safe_get(cf, i, "Net Income", 0), depreciation_and_amortization=0.0, deferred_income_tax=0.0,
            stock_based_compensation=0.0, change_in_working_capital=0.0, accounts_receivables=0.0, inventory=0.0,
            accounts_payables=0.0, other_working_capital=0.0, other_non_cash_items=0.0,
            net_cash_provided_by_operating_activities=ocf, investments_in_property_plant_and_equipment=0.0,
            acquisitions_net=0.0, purchases_of_investments=0.0, sales_maturities_of_investments=0.0,
            other_investing_activites=0.0, net_cash_used_for_investing_activites=0.0, debt_repayment=0.0,
            common_stock_issued=0.0, common_stock_repurchased=0.0, dividends_paid=0.0, other_financing_activites=0.0,
            net_cash_used_provided_by_financing_activities=0.0, effect_of_forex_changes_on_cash=0.0, net_change_in_cash=0.0,
            cash_at_end_of_period=0.0, cash_at_beginning_of_period=0.0, operating_cash_flow=ocf, free_cash_flow=fcf
        )
        cfs.append(cf_obj)
        
    mock_md.get_income_statements.return_value = incs
    mock_md.get_balance_sheets.return_value = bals
    mock_md.get_cash_flow_statements.return_value = cfs
    
    # 6. Historical Prices
    hist_list = []
    hist.dropna(subset=['Open', 'High', 'Low', 'Close', 'Volume'], inplace=True)
    for index, row in hist.iterrows():
        hist_list.append(HistoricalPrice(
            date=str(index),
            open=row["Open"],
            high=row["High"],
            low=row["Low"],
            close=row["Close"],
            volume=row["Volume"]
        ))
    hist_series = HistoricalPriceSeries(ticker=ticker, prices=hist_list)
    mock_md.get_historical_prices.return_value = hist_series
    
    # 7. Dividends
    div_list = []
    if len(data["dividends"]) > 0:
        for index, val in data["dividends"].items():
            div_list.append(DividendHistory(
                date=str(index), symbol=ticker, label="Dividend", adj_dividend=val, amount=val, record_date=str(index), payment_date=str(index), declaration_date=str(index)
            ))
    div_list.reverse() # Newest first
    mock_md.get_dividend_history.return_value = div_list
    
    engine = AnalysisEngine(market_data_service=mock_md)
    report = await engine.generate_full_report(ticker)
    
    # --- Validations ---
    # WACC should be between 2% and 30% for these massive companies
    assert 0.02 < report.valuation.wacc < 0.30
    
    # DCF Intrinsic value should be a positive number
    assert report.valuation.dcf_intrinsic_value > 0
    
    # If they pay dividends, DDM intrinsic value should be positive
    if len(div_list) > 0:
        if report.valuation.ddm_intrinsic_value is not None:
            assert report.valuation.ddm_intrinsic_value > 0
            
    # Risk Beta should be a reasonable range (0.1 to 3.0)
    assert 0.1 <= report.risk.beta <= 3.0
    
    # Overall Score should be between 0 and 100
    assert 0 <= report.scores.overall_score.score <= 100
