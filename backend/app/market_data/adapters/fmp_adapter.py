from typing import List, Optional
from datetime import datetime
from app.market_data.interfaces import ProviderInterface
from app.market_data.adapters.base import BaseAdapter
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

class FMPAdapter(BaseAdapter, ProviderInterface):
    """
    Adapter for Financial Modeling Prep (FMP) API.
    """
    def __init__(self, api_key: str):
        super().__init__(base_url="https://financialmodelingprep.com/api/v3", api_key=api_key)

    def _auth_params(self) -> dict:
        return {"apikey": self.api_key}

    async def get_company_profile(self, ticker: str) -> Optional[CompanyProfile]:
        endpoint = f"/profile/{ticker.upper()}"
        data = await self._get(endpoint, params=self._auth_params())
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        raw = data[0]
        return CompanyProfile(
            ticker=raw.get("symbol", ticker),
            company_name=raw.get("companyName", ""),
            currency=raw.get("currency"),
            exchange=raw.get("exchangeShortName"),
            industry=raw.get("industry"),
            sector=raw.get("sector"),
            website=raw.get("website"),
            description=raw.get("description"),
            ceo=raw.get("ceo"),
            market_cap=raw.get("mktCap"),
            beta=raw.get("beta"),
            price=raw.get("price"),
            image=raw.get("image"),
            is_actively_trading=raw.get("isActivelyTrading")
        )

    async def get_quote(self, ticker: str) -> Optional[StockQuote]:
        endpoint = f"/quote/{ticker.upper()}"
        data = await self._get(endpoint, params=self._auth_params())
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        raw = data[0]
        return StockQuote(
            ticker=raw.get("symbol", ticker),
            price=raw.get("price", 0.0),
            change=raw.get("change"),
            change_percent=raw.get("changesPercentage"),
            day_low=raw.get("dayLow"),
            day_high=raw.get("dayHigh"),
            year_low=raw.get("yearLow"),
            year_high=raw.get("yearHigh"),
            market_cap=raw.get("marketCap"),
            volume=raw.get("volume"),
            avg_volume=raw.get("avgVolume"),
            exchange=raw.get("exchange"),
            timestamp=raw.get("timestamp")
        )

    async def get_historical_prices(self, ticker: str, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Optional[HistoricalPriceSeries]:
        endpoint = f"/historical-price-full/{ticker.upper()}"
        params = self._auth_params()
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
            
        data = await self._get(endpoint, params=params)
        if not data or "historical" not in data:
            return None
            
        prices = []
        for raw in data["historical"]:
            prices.append(HistoricalPrice(
                date=raw.get("date"),
                open=raw.get("open", 0.0),
                high=raw.get("high", 0.0),
                low=raw.get("low", 0.0),
                close=raw.get("close", 0.0),
                adj_close=raw.get("adjClose"),
                volume=raw.get("volume", 0),
                unadjusted_volume=raw.get("unadjustedVolume"),
                change=raw.get("change"),
                change_percent=raw.get("changePercent"),
                vwap=raw.get("vwap")
            ))
            
        return HistoricalPriceSeries(ticker=data.get("symbol", ticker), prices=prices)

    async def get_income_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[IncomeStatement]:
        endpoint = f"/income-statement/{ticker.upper()}"
        params = self._auth_params()
        params["limit"] = limit
        if period != "annual":
            params["period"] = period
            
        data = await self._get(endpoint, params=params)
        if not data:
            return []
            
        return [IncomeStatement(
            date=raw.get("date", ""),
            symbol=raw.get("symbol", ticker),
            reported_currency=raw.get("reportedCurrency", ""),
            cik=raw.get("cik", ""),
            filling_date=raw.get("fillingDate", ""),
            accepted_date=raw.get("acceptedDate", ""),
            calendar_year=raw.get("calendarYear", ""),
            period=raw.get("period", ""),
            revenue=raw.get("revenue", 0.0),
            cost_of_revenue=raw.get("costOfRevenue", 0.0),
            gross_profit=raw.get("grossProfit", 0.0),
            gross_profit_ratio=raw.get("grossProfitRatio", 0.0),
            research_and_development_expenses=raw.get("researchAndDevelopmentExpenses", 0.0),
            general_and_administrative_expenses=raw.get("generalAndAdministrativeExpenses", 0.0),
            selling_and_marketing_expenses=raw.get("sellingAndMarketingExpenses", 0.0),
            selling_general_and_administrative_expenses=raw.get("sellingGeneralAndAdministrativeExpenses", 0.0),
            other_expenses=raw.get("otherExpenses", 0.0),
            operating_expenses=raw.get("operatingExpenses", 0.0),
            cost_and_expenses=raw.get("costAndExpenses", 0.0),
            interest_income=raw.get("interestIncome", 0.0),
            interest_expense=raw.get("interestExpense", 0.0),
            depreciation_and_amortization=raw.get("depreciationAndAmortization", 0.0),
            ebitda=raw.get("ebitda", 0.0),
            ebitdaratio=raw.get("ebitdaratio", 0.0),
            operating_income=raw.get("operatingIncome", 0.0),
            operating_income_ratio=raw.get("operatingIncomeRatio", 0.0),
            total_other_income_expenses_net=raw.get("totalOtherIncomeExpensesNet", 0.0),
            income_before_tax=raw.get("incomeBeforeTax", 0.0),
            income_before_tax_ratio=raw.get("incomeBeforeTaxRatio", 0.0),
            income_tax_expense=raw.get("incomeTaxExpense", 0.0),
            net_income=raw.get("netIncome", 0.0),
            net_income_ratio=raw.get("netIncomeRatio", 0.0),
            eps=raw.get("eps", 0.0),
            epsdiluted=raw.get("epsdiluted", 0.0),
            weighted_average_shs_out=raw.get("weightedAverageShsOut", 0.0),
            weighted_average_shs_out_dil=raw.get("weightedAverageShsOutDil", 0.0)
        ) for raw in data]

    async def get_balance_sheets(self, ticker: str, limit: int = 4, period: str = "annual") -> List[BalanceSheet]:
        endpoint = f"/balance-sheet-statement/{ticker.upper()}"
        params = self._auth_params()
        params["limit"] = limit
        if period != "annual":
            params["period"] = period
            
        data = await self._get(endpoint, params=params)
        if not data:
            return []
            
        return [BalanceSheet(
            date=raw.get("date", ""),
            symbol=raw.get("symbol", ticker),
            reported_currency=raw.get("reportedCurrency", ""),
            cik=raw.get("cik", ""),
            filling_date=raw.get("fillingDate", ""),
            accepted_date=raw.get("acceptedDate", ""),
            calendar_year=raw.get("calendarYear", ""),
            period=raw.get("period", ""),
            cash_and_cash_equivalents=raw.get("cashAndCashEquivalents", 0.0),
            short_term_investments=raw.get("shortTermInvestments", 0.0),
            cash_and_short_term_investments=raw.get("cashAndShortTermInvestments", 0.0),
            net_receivables=raw.get("netReceivables", 0.0),
            inventory=raw.get("inventory", 0.0),
            other_current_assets=raw.get("otherCurrentAssets", 0.0),
            total_current_assets=raw.get("totalCurrentAssets", 0.0),
            property_plant_equipment_net=raw.get("propertyPlantEquipmentNet", 0.0),
            goodwill=raw.get("goodwill", 0.0),
            intangible_assets=raw.get("intangibleAssets", 0.0),
            long_term_investments=raw.get("longTermInvestments", 0.0),
            tax_assets=raw.get("taxAssets", 0.0),
            other_non_current_assets=raw.get("otherNonCurrentAssets", 0.0),
            total_non_current_assets=raw.get("totalNonCurrentAssets", 0.0),
            other_assets=raw.get("otherAssets", 0.0),
            total_assets=raw.get("totalAssets", 0.0),
            account_payables=raw.get("accountPayables", 0.0),
            short_term_debt=raw.get("shortTermDebt", 0.0),
            tax_payables=raw.get("taxPayables", 0.0),
            deferred_revenue=raw.get("deferredRevenue", 0.0),
            other_current_liabilities=raw.get("otherCurrentLiabilities", 0.0),
            total_current_liabilities=raw.get("totalCurrentLiabilities", 0.0),
            long_term_debt=raw.get("longTermDebt", 0.0),
            deferred_revenue_non_current=raw.get("deferredRevenueNonCurrent", 0.0),
            deferred_tax_liabilities_non_current=raw.get("deferredTaxLiabilitiesNonCurrent", 0.0),
            other_non_current_liabilities=raw.get("otherNonCurrentLiabilities", 0.0),
            total_non_current_liabilities=raw.get("totalNonCurrentLiabilities", 0.0),
            other_liabilities=raw.get("otherLiabilities", 0.0),
            capital_lease_obligations=raw.get("capitalLeaseObligations", 0.0),
            total_liabilities=raw.get("totalLiabilities", 0.0),
            preferred_stock=raw.get("preferredStock", 0.0),
            common_stock=raw.get("commonStock", 0.0),
            retained_earnings=raw.get("retainedEarnings", 0.0),
            accumulated_other_comprehensive_income_loss=raw.get("accumulatedOtherComprehensiveIncomeLoss", 0.0),
            othertotal_stockholders_equity=raw.get("othertotalStockholdersEquity", 0.0),
            total_stockholders_equity=raw.get("totalStockholdersEquity", 0.0),
            total_equity=raw.get("totalEquity", 0.0),
            total_liabilities_and_stockholders_equity=raw.get("totalLiabilitiesAndStockholdersEquity", 0.0),
            minority_interest=raw.get("minorityInterest", 0.0),
            total_liabilities_and_total_equity=raw.get("totalLiabilitiesAndTotalEquity", 0.0),
            total_investments=raw.get("totalInvestments", 0.0),
            total_debt=raw.get("totalDebt", 0.0),
            net_debt=raw.get("netDebt", 0.0)
        ) for raw in data]

    async def get_cash_flow_statements(self, ticker: str, limit: int = 4, period: str = "annual") -> List[CashFlowStatement]:
        endpoint = f"/cash-flow-statement/{ticker.upper()}"
        params = self._auth_params()
        params["limit"] = limit
        if period != "annual":
            params["period"] = period
            
        data = await self._get(endpoint, params=params)
        if not data:
            return []
            
        return [CashFlowStatement(
            date=raw.get("date", ""),
            symbol=raw.get("symbol", ticker),
            reported_currency=raw.get("reportedCurrency", ""),
            cik=raw.get("cik", ""),
            filling_date=raw.get("fillingDate", ""),
            accepted_date=raw.get("acceptedDate", ""),
            calendar_year=raw.get("calendarYear", ""),
            period=raw.get("period", ""),
            net_income=raw.get("netIncome", 0.0),
            depreciation_and_amortization=raw.get("depreciationAndAmortization", 0.0),
            deferred_income_tax=raw.get("deferredIncomeTax", 0.0),
            stock_based_compensation=raw.get("stockBasedCompensation", 0.0),
            change_in_working_capital=raw.get("changeInWorkingCapital", 0.0),
            accounts_receivables=raw.get("accountsReceivables", 0.0),
            inventory=raw.get("inventory", 0.0),
            accounts_payables=raw.get("accountsPayables", 0.0),
            other_working_capital=raw.get("otherWorkingCapital", 0.0),
            other_non_cash_items=raw.get("otherNonCashItems", 0.0),
            net_cash_provided_by_operating_activities=raw.get("netCashProvidedByOperatingActivities", 0.0),
            investments_in_property_plant_and_equipment=raw.get("investmentsInPropertyPlantAndEquipment", 0.0),
            acquisitions_net=raw.get("acquisitionsNet", 0.0),
            purchases_of_investments=raw.get("purchasesOfInvestments", 0.0),
            sales_maturities_of_investments=raw.get("salesMaturitiesOfInvestments", 0.0),
            other_investing_activites=raw.get("otherInvestingActivites", 0.0),
            net_cash_used_for_investing_activites=raw.get("netCashUsedForInvestingActivites", 0.0),
            debt_repayment=raw.get("debtRepayment", 0.0),
            common_stock_issued=raw.get("commonStockIssued", 0.0),
            common_stock_repurchased=raw.get("commonStockRepurchased", 0.0),
            dividends_paid=raw.get("dividendsPaid", 0.0),
            other_financing_activites=raw.get("otherFinancingActivites", 0.0),
            net_cash_used_provided_by_financing_activities=raw.get("netCashUsedProvidedByFinancingActivities", 0.0),
            effect_of_forex_changes_on_cash=raw.get("effectOfForexChangesOnCash", 0.0),
            net_change_in_cash=raw.get("netChangeInCash", 0.0),
            cash_at_end_of_period=raw.get("cashAtEndOfPeriod", 0.0),
            cash_at_beginning_of_period=raw.get("cashAtBeginningOfPeriod", 0.0),
            operating_cash_flow=raw.get("operatingCashFlow", 0.0),
            capital_expenditure=raw.get("capitalExpenditure", 0.0),
            free_cash_flow=raw.get("freeCashFlow", 0.0)
        ) for raw in data]
