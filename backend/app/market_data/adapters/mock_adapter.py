from typing import List, Optional
from datetime import datetime, timedelta
from app.market_data.interfaces import ProviderInterface
from app.market_data.models import (
    CompanyProfile,
    StockQuote,
    HistoricalPrice,
    HistoricalPriceSeries,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    CompanySearchResult,
    FinancialRatios,
    MarketNews,
    EconomicIndicator,
    ExchangeRate,
    EarningsEvent,
    DividendHistory,
    StockSplit,
    MarketIndex,
    SectorIndustryClass
)
from app.core.exceptions import FinPilotException

class MockAdapter(ProviderInterface):
    """
    Mock Adapter for local testing and CI/CD without external API keys.
    Returns deterministic, realistic fake data.
    """
    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        if ticker.upper() == "UNKNOWN":
            return None
            
        return CompanyProfile(
            ticker=ticker.upper(),
            company_name=f"{ticker.upper()} Corporation",
            currency="USD",
            exchange="NASDAQ",
            industry="Technology",
            sector="Software",
            website=f"https://www.{ticker.lower()}.mock",
            description="A mock technology company used for testing.",
            ceo="Jane Doe",
            market_cap=1000000000000.0,
            beta=1.2,
            price=150.00,
            image=None,
            is_actively_trading=True
        )

    async def get_quote(self, ticker: str) -> Optional[StockQuote]:
        if ticker.upper() == "UNKNOWN":
            return None
            
        return StockQuote(
            ticker=ticker.upper(),
            price=150.50,
            change=2.50,
            change_percent=1.69,
            day_low=148.00,
            day_high=151.00,
            year_low=100.00,
            year_high=160.00,
            market_cap=1000000000000.0,
            volume=50000000,
            avg_volume=45000000,
            exchange="NASDAQ",
            timestamp=int(datetime.now().timestamp())
        )

    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]:
        if ticker.upper() == "UNKNOWN":
            return None
            
        prices = []
        base_price = 150.0
        start = datetime.now() - timedelta(days=30)
        
        for i in range(30):
            current_date = start + timedelta(days=i)
            # Skip weekends
            if current_date.weekday() > 4:
                continue
                
            prices.append(HistoricalPrice(
                date=current_date.strftime("%Y-%m-%d"),
                open=base_price,
                high=base_price + 2.0,
                low=base_price - 1.0,
                close=base_price + 1.0,
                adj_close=base_price + 1.0,
                volume=10000000
            ))
            base_price += 0.5 # Upward trend
            
        return HistoricalPriceSeries(ticker=ticker.upper(), prices=prices[::-1]) # Descending

    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]:
        if ticker.upper() == "UNKNOWN":
            return []
            
        statements = []
        for i in range(limit):
            year = 2023 - i
            statements.append(IncomeStatement(
                date=f"{year}-12-31",
                symbol=ticker.upper(),
                reported_currency="USD",
                cik="0001234567",
                filling_date=f"{year+1}-02-15",
                accepted_date=f"{year+1}-02-15",
                calendar_year=str(year),
                period="FY" if period == "annual" else "Q4",
                revenue=10000000000.0,
                cost_of_revenue=4000000000.0,
                gross_profit=6000000000.0,
                gross_profit_ratio=0.6,
                research_and_development_expenses=1000000000.0,
                general_and_administrative_expenses=500000000.0,
                selling_and_marketing_expenses=500000000.0,
                selling_general_and_administrative_expenses=1000000000.0,
                other_expenses=0.0,
                operating_expenses=2000000000.0,
                cost_and_expenses=6000000000.0,
                interest_income=10000000.0,
                interest_expense=50000000.0,
                depreciation_and_amortization=200000000.0,
                ebitda=4200000000.0,
                ebitdaratio=0.42,
                operating_income=4000000000.0,
                operating_income_ratio=0.4,
                total_other_income_expenses_net=-40000000.0,
                income_before_tax=3960000000.0,
                income_before_tax_ratio=0.396,
                income_tax_expense=792000000.0,
                net_income=3168000000.0,
                net_income_ratio=0.3168,
                eps=3.16,
                epsdiluted=3.15,
                weighted_average_shs_out=1000000000.0,
                weighted_average_shs_out_dil=1005000000.0
            ))
        return statements

    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]:
        if ticker.upper() == "UNKNOWN":
            return []
            
        statements = []
        for i in range(limit):
            year = 2023 - i
            statements.append(BalanceSheet(
                date=f"{year}-12-31",
                symbol=ticker.upper(),
                reported_currency="USD",
                cik="0001234567",
                filling_date=f"{year+1}-02-15",
                accepted_date=f"{year+1}-02-15",
                calendar_year=str(year),
                period="FY" if period == "annual" else "Q4",
                cash_and_cash_equivalents=5000000000.0,
                short_term_investments=2000000000.0,
                cash_and_short_term_investments=7000000000.0,
                net_receivables=1500000000.0,
                inventory=1000000000.0,
                other_current_assets=500000000.0,
                total_current_assets=10000000000.0,
                property_plant_equipment_net=4000000000.0,
                goodwill=1000000000.0,
                intangible_assets=500000000.0,
                long_term_investments=2000000000.0,
                tax_assets=100000000.0,
                other_non_current_assets=400000000.0,
                total_non_current_assets=8000000000.0,
                other_assets=0.0,
                total_assets=18000000000.0,
                account_payables=1000000000.0,
                short_term_debt=500000000.0,
                tax_payables=200000000.0,
                deferred_revenue=300000000.0,
                other_current_liabilities=1000000000.0,
                total_current_liabilities=3000000000.0,
                long_term_debt=4000000000.0,
                deferred_revenue_non_current=0.0,
                deferred_tax_liabilities_non_current=0.0,
                other_non_current_liabilities=1000000000.0,
                total_non_current_liabilities=5000000000.0,
                other_liabilities=0.0,
                capital_lease_obligations=0.0,
                total_liabilities=8000000000.0,
                preferred_stock=0.0,
                common_stock=1000000000.0,
                retained_earnings=9000000000.0,
                accumulated_other_comprehensive_income_loss=0.0,
                othertotal_stockholders_equity=0.0,
                total_stockholders_equity=10000000000.0,
                total_equity=10000000000.0,
                total_liabilities_and_stockholders_equity=18000000000.0,
                minority_interest=0.0,
                total_liabilities_and_total_equity=18000000000.0,
                total_investments=4000000000.0,
                total_debt=4500000000.0,
                net_debt=-500000000.0
            ))
        return statements

    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]:
        if ticker.upper() == "UNKNOWN":
            return []
            
        statements = []
        for i in range(limit):
            year = 2023 - i
            statements.append(CashFlowStatement(
                date=f"{year}-12-31",
                symbol=ticker.upper(),
                reported_currency="USD",
                cik="0001234567",
                filling_date=f"{year+1}-02-15",
                accepted_date=f"{year+1}-02-15",
                calendar_year=str(year),
                period="FY" if period == "annual" else "Q4",
                net_income=3168000000.0,
                depreciation_and_amortization=200000000.0,
                deferred_income_tax=50000000.0,
                stock_based_compensation=100000000.0,
                change_in_working_capital=200000000.0,
                accounts_receivables=-50000000.0,
                inventory=-100000000.0,
                accounts_payables=100000000.0,
                other_working_capital=250000000.0,
                other_non_cash_items=0.0,
                net_cash_provided_by_operating_activities=3718000000.0,
                investments_in_property_plant_and_equipment=-500000000.0,
                acquisitions_net=-100000000.0,
                purchases_of_investments=-1000000000.0,
                sales_maturities_of_investments=800000000.0,
                other_investing_activites=0.0,
                net_cash_used_for_investing_activites=-800000000.0,
                debt_repayment=-200000000.0,
                common_stock_issued=0.0,
                common_stock_repurchased=-500000000.0,
                dividends_paid=-1000000000.0,
                other_financing_activites=0.0,
                net_cash_used_provided_by_financing_activities=-1700000000.0,
                effect_of_forex_changes_on_cash=-18000000.0,
                net_change_in_cash=1200000000.0,
                cash_at_end_of_period=5000000000.0,
                cash_at_beginning_of_period=3800000000.0,
                operating_cash_flow=3718000000.0,
                capital_expenditure=-500000000.0,
                free_cash_flow=3218000000.0
            ))
        return statements

    async def search_company(self, query: str) -> List[CompanySearchResult]:
        if query == "FAIL_SEARCH": raise FinPilotException(status_code=500, message="Mock Search Failure")
        return [CompanySearchResult(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ")]

    async def get_financial_ratios(self, ticker: str) -> List[FinancialRatios]:
        if ticker == "FAIL": raise FinPilotException(status_code=500, message="Mock Ratios Failure")
        if ticker == "UNKNOWN": return []
        return [FinancialRatios(symbol=ticker, date="2023-12-31", pe_ratio=25.5, pb_ratio=10.2)]

    async def get_market_news(self, ticker: str, limit: int = 10) -> List[MarketNews]:
        if ticker == "FAIL": raise FinPilotException(status_code=500, message="Mock News Failure")
        if ticker == "UNKNOWN": return []
        return [MarketNews(id="1", symbol=ticker, title="Mock News", published_at="2023-10-01", source="MockSource", url="https://example.com/news")]

    async def get_economic_indicator(self, indicator: str) -> List[EconomicIndicator]:
        if indicator == "FAIL": raise FinPilotException(status_code=500, message="Mock FRED Failure")
        return [EconomicIndicator(indicator_id=indicator, name=indicator, date="2023-10-01", value=2.5)]

    async def get_exchange_rate(self, base_currency: str, target_currency: str) -> Optional[ExchangeRate]:
        if base_currency == "FAIL": raise FinPilotException(status_code=500, message="Mock Exchange Failure")
        return ExchangeRate(base_currency=base_currency, target_currency=target_currency, rate=1.2, timestamp="2023-10-01T00:00:00Z")

    async def get_earnings_calendar(self, ticker: str) -> List[EarningsEvent]:
        if ticker == "UNKNOWN": return []
        return [EarningsEvent(symbol=ticker, date="2023-10-01", eps_estimate=1.5, eps_actual=1.6)]

    async def get_dividend_history(self, ticker: str) -> List[DividendHistory]:
        if ticker == "UNKNOWN": return []
        return [DividendHistory(symbol=ticker, date="2023-10-01", amount=0.5)]

    async def get_stock_splits(self, ticker: str) -> List[StockSplit]:
        if ticker == "UNKNOWN": return []
        return [StockSplit(symbol=ticker, date="2023-10-01", numerator=4.0, denominator=1.0)]

    async def get_market_indices(self) -> List[MarketIndex]:
        return [MarketIndex(symbol="^GSPC", name="S&P 500", price=4500.0, change=10.0, change_percent=0.2)]

    async def get_sector_industry(self, ticker: str) -> Optional[SectorIndustryClass]:
        if ticker == "UNKNOWN": return None
        return SectorIndustryClass(symbol=ticker, sector="Technology", industry="Consumer Electronics")
