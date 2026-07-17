import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import Response, HTTPStatusError, Request, RequestError
from app.market_data.adapters.mock_adapter import MockAdapter
from app.market_data.adapters.fmp_adapter import FMPAdapter
from app.market_data.adapters.finnhub_adapter import FinnhubAdapter
from app.market_data.adapters.alphavantage_adapter import AlphaVantageAdapter
from app.core.exceptions import FinPilotException
from app.market_data.service import MarketDataService
from app.market_data.models import CompanyProfile

@pytest.fixture
def fmp_adapter():
    return FMPAdapter(api_key="test_key")

@pytest.mark.asyncio
async def test_base_adapter_http_error(fmp_adapter):
    with patch("httpx.AsyncClient.get") as mock_get:
        # Simulate 404
        mock_get.return_value = Response(404, request=Request("GET", "url"))
        result = await fmp_adapter._get("/profile/AAPL")
        assert result is None
        
        # Simulate 429
        mock_get.return_value = Response(429, request=Request("GET", "url"))
        mock_get.return_value.raise_for_status = MagicMock(side_effect=HTTPStatusError("429", request=mock_get.return_value.request, response=mock_get.return_value))
        with pytest.raises(FinPilotException) as exc:
            await fmp_adapter._get("/profile/AAPL")
        assert exc.value.status_code == 429
        
        # Simulate 401
        mock_get.return_value = Response(401, request=Request("GET", "url"))
        mock_get.return_value.raise_for_status = MagicMock(side_effect=HTTPStatusError("401", request=mock_get.return_value.request, response=mock_get.return_value))
        with pytest.raises(FinPilotException) as exc:
            await fmp_adapter._get("/profile/AAPL")
        assert exc.value.status_code == 500
        
        # Simulate general 500
        mock_get.return_value = Response(500, request=Request("GET", "url"))
        mock_get.return_value.raise_for_status = MagicMock(side_effect=HTTPStatusError("500", request=mock_get.return_value.request, response=mock_get.return_value))
        with pytest.raises(FinPilotException) as exc:
            await fmp_adapter._get("/profile/AAPL")
        assert exc.value.status_code == 502
        
        # Simulate network error
        mock_get.side_effect = RequestError("Network error", request=Request("GET", "url"))
        with pytest.raises(FinPilotException) as exc:
            await fmp_adapter._get("/profile/AAPL")
        assert exc.value.status_code == 504

@pytest.mark.asyncio
async def test_fmp_adapter_parsing(fmp_adapter):
    with patch.object(fmp_adapter, "_get", new_callable=AsyncMock) as mock_get:
        # Profile
        mock_get.return_value = [{"symbol": "AAPL", "companyName": "Apple Inc.", "price": 150.0}]
        profile = await fmp_adapter.get_company_profile("AAPL")
        assert profile.ticker == "AAPL"
        assert profile.company_name == "Apple Inc."
        
        # Empty profile
        mock_get.return_value = []
        profile = await fmp_adapter.get_company_profile("UNKNOWN")
        assert profile is None
        
        # Quote
        mock_get.return_value = [{"symbol": "AAPL", "price": 150.0}]
        quote = await fmp_adapter.get_quote("AAPL")
        assert quote.price == 150.0
        
        # Empty quote
        mock_get.return_value = []
        quote = await fmp_adapter.get_quote("UNKNOWN")
        assert quote is None
        
        # Historical
        mock_get.return_value = {"symbol": "AAPL", "historical": [{"date": "2023-01-01", "close": 150.0, "volume": 100}]}
        hist = await fmp_adapter.get_historical_prices("AAPL", from_date="2023-01-01")
        assert hist.prices[0].close == 150.0
        
        # Empty historical
        mock_get.return_value = {}
        hist = await fmp_adapter.get_historical_prices("UNKNOWN")
        assert hist is None
        
        # Income Statement
        mock_get.return_value = [{"date": "2023-12-31", "symbol": "AAPL", "revenue": 1000.0, "reportedCurrency": "USD", "cik": "123", "fillingDate": "", "acceptedDate": "", "calendarYear": "2023", "period": "FY", "costOfRevenue": 500, "grossProfit": 500, "grossProfitRatio": 0.5, "researchAndDevelopmentExpenses": 100, "generalAndAdministrativeExpenses": 50, "sellingAndMarketingExpenses": 50, "sellingGeneralAndAdministrativeExpenses": 100, "otherExpenses": 0, "operatingExpenses": 200, "costAndExpenses": 700, "interestIncome": 10, "interestExpense": 20, "depreciationAndAmortization": 30, "ebitda": 300, "ebitdaratio": 0.3, "operatingIncome": 270, "operatingIncomeRatio": 0.27, "totalOtherIncomeExpensesNet": -10, "incomeBeforeTax": 260, "incomeBeforeTaxRatio": 0.26, "incomeTaxExpense": 60, "netIncome": 200, "netIncomeRatio": 0.2, "eps": 2.0, "epsdiluted": 1.9, "weightedAverageShsOut": 100, "weightedAverageShsOutDil": 105}]
        inc = await fmp_adapter.get_income_statements("AAPL")
        assert inc[0].revenue == 1000.0
        
        # Empty income
        mock_get.return_value = []
        inc = await fmp_adapter.get_income_statements("UNKNOWN")
        assert inc == []
        
        # Balance Sheet
        mock_get.return_value = [{"date": "2023-12-31", "symbol": "AAPL", "totalAssets": 5000.0, "reportedCurrency": "USD", "cik": "123", "fillingDate": "", "acceptedDate": "", "calendarYear": "2023", "period": "FY", "cashAndCashEquivalents": 100, "shortTermInvestments": 100, "cashAndShortTermInvestments": 200, "netReceivables": 100, "inventory": 100, "otherCurrentAssets": 100, "totalCurrentAssets": 500, "propertyPlantEquipmentNet": 500, "goodwill": 100, "intangibleAssets": 100, "longTermInvestments": 100, "taxAssets": 100, "otherNonCurrentAssets": 100, "totalNonCurrentAssets": 1000, "otherAssets": 0, "accountPayables": 100, "shortTermDebt": 100, "taxPayables": 100, "deferredRevenue": 100, "otherCurrentLiabilities": 100, "totalCurrentLiabilities": 500, "longTermDebt": 1000, "deferredRevenueNonCurrent": 100, "deferredTaxLiabilitiesNonCurrent": 100, "otherNonCurrentLiabilities": 100, "totalNonCurrentLiabilities": 1300, "otherLiabilities": 0, "capitalLeaseObligations": 0, "totalLiabilities": 1800, "preferredStock": 0, "commonStock": 1000, "retainedEarnings": 2200, "accumulatedOtherComprehensiveIncomeLoss": 0, "othertotalStockholdersEquity": 0, "totalStockholdersEquity": 3200, "totalEquity": 3200, "totalLiabilitiesAndStockholdersEquity": 5000, "minorityInterest": 0, "totalLiabilitiesAndTotalEquity": 5000, "totalInvestments": 200, "totalDebt": 1100, "netDebt": 900}]
        bal = await fmp_adapter.get_balance_sheets("AAPL")
        assert bal[0].total_assets == 5000.0
        
        # Empty balance
        mock_get.return_value = []
        bal = await fmp_adapter.get_balance_sheets("UNKNOWN")
        assert bal == []
        
        # Cash Flow
        mock_get.return_value = [{"date": "2023-12-31", "symbol": "AAPL", "freeCashFlow": 1500.0, "reportedCurrency": "USD", "cik": "123", "fillingDate": "", "acceptedDate": "", "calendarYear": "2023", "period": "FY", "netIncome": 1000, "depreciationAndAmortization": 100, "deferredIncomeTax": 100, "stockBasedCompensation": 100, "changeInWorkingCapital": 100, "accountsReceivables": 100, "inventory": 100, "accountsPayables": 100, "otherWorkingCapital": 100, "otherNonCashItems": 0, "netCashProvidedByOperatingActivities": 1400, "investmentsInPropertyPlantAndEquipment": 100, "acquisitionsNet": 100, "purchasesOfInvestments": 100, "salesMaturitiesOfInvestments": 100, "otherInvestingActivites": 0, "netCashUsedForInvestingActivites": 400, "debtRepayment": 100, "commonStockIssued": 0, "commonStockRepurchased": 100, "dividendsPaid": 100, "otherFinancingActivites": 0, "netCashUsedProvidedByFinancingActivities": 300, "effectOfForexChangesOnCash": 0, "netChangeInCash": 700, "cashAtEndOfPeriod": 1700, "cashAtBeginningOfPeriod": 1000, "operatingCashFlow": 1400, "capitalExpenditure": 100}]
        cf = await fmp_adapter.get_cash_flow_statements("AAPL")
        assert cf[0].free_cash_flow == 1500.0
        
        # Empty cash flow
        mock_get.return_value = []
        cf = await fmp_adapter.get_cash_flow_statements("UNKNOWN")
        assert cf == []

@pytest.mark.asyncio
async def test_market_data_service_caching_and_fallback():
    service = MarketDataService()
    # Prevent aliasing with self.mock in test environments without API keys
    service.fmp = FMPAdapter(api_key="test")
    service.finnhub = FinnhubAdapter(api_key="test")
    service.alpha_vantage = AlphaVantageAdapter(api_key="test")
    
    # Force all providers to throw an exception to test fallback
    with patch.object(service.fmp, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=500, message="FMP Down")), \
         patch.object(service.finnhub, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=500, message="Finnhub Down")), \
         patch.object(service.alpha_vantage, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=500, message="AV Down")), \
         patch.object(service.mock, 'get_company_profile', new_callable=AsyncMock, return_value=CompanyProfile(ticker="FALLBACK", company_name="Fallback")):
        
        result = await service.get_company_profile("PROVIDERS_FALLBACK_TEST")
        assert result.ticker == "FALLBACK"

    # Second call should hit the cache! We can verify by making all throw exceptions
    # If it hits the cache, it won't execute either
    with patch.object(service.fmp, 'get_company_profile', new_callable=AsyncMock, side_effect=Exception("Should not hit")), \
         patch.object(service.finnhub, 'get_company_profile', new_callable=AsyncMock, side_effect=Exception("Should not hit")), \
         patch.object(service.alpha_vantage, 'get_company_profile', new_callable=AsyncMock, side_effect=Exception("Should not hit")), \
         patch.object(service.mock, 'get_company_profile', new_callable=AsyncMock, side_effect=Exception("Should not hit")):
        cached_profile = await service.get_company_profile("PROVIDERS_FALLBACK_TEST")
        assert cached_profile is not None
        assert cached_profile.ticker == "FALLBACK"

    # Test cache lists (income statements)
    with patch.object(service.fmp, 'get_income_statements', new_callable=AsyncMock, side_effect=Exception("Primary Down")):
        statements = await service.get_income_statements("NEW_INCOME_TEST", limit=1)
        assert len(statements) > 0

    with patch.object(service.fmp, 'get_income_statements', new_callable=AsyncMock, side_effect=Exception("Should not hit")), \
         patch.object(service.mock, 'get_income_statements', new_callable=AsyncMock, side_effect=Exception("Should not hit")):
        cached_statements = await service.get_income_statements("NEW_INCOME_TEST", limit=1)
        assert len(cached_statements) > 0

@pytest.mark.asyncio
async def test_cache_miss_malformed_data():
    service = MarketDataService()
    await service.cache.redis.set("md:profile:MALFORMED", "{invalid_json")
    
    # Should safely return None from cache, and then fetch from provider
    profile = await service.get_company_profile("MALFORMED")
    assert profile.ticker == "MALFORMED"
    
    await service.cache.redis.set("md:income:MALFORMED:annual:4", "{invalid_list")
    statements = await service.get_income_statements("MALFORMED", limit=4)
    assert len(statements) > 0
