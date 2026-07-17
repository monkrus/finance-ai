import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_company_profile(client: AsyncClient):
    response = await client.get("/api/v1/market-data/profile/AAPL")
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"

@pytest.mark.asyncio
async def test_get_stock_quote(client: AsyncClient):
    response = await client.get("/api/v1/market-data/quote/AAPL")
    assert response.status_code == 200
    assert response.json()["ticker"] == "AAPL"

@pytest.mark.asyncio
async def test_get_historical_prices(client: AsyncClient):
    response = await client.get("/api/v1/market-data/historical/AAPL")
    assert response.status_code == 200
    assert len(response.json()["prices"]) > 0

@pytest.mark.asyncio
async def test_get_income_statements(client: AsyncClient):
    response = await client.get("/api/v1/market-data/financials/AAPL/income?limit=1")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_balance_sheets(client: AsyncClient):
    response = await client.get("/api/v1/market-data/financials/AAPL/balance-sheet?limit=1")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_cash_flow_statements(client: AsyncClient):
    response = await client.get("/api/v1/market-data/financials/AAPL/cash-flow?limit=1")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_search_company(client: AsyncClient):
    response = await client.get("/api/v1/market-data/search?query=Apple")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_financial_ratios(client: AsyncClient):
    response = await client.get("/api/v1/market-data/ratios/AAPL")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_market_news(client: AsyncClient):
    response = await client.get("/api/v1/market-data/news/AAPL")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_economic_indicator(client: AsyncClient):
    response = await client.get("/api/v1/market-data/economic/GDP")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_exchange_rate(client: AsyncClient):
    response = await client.get("/api/v1/market-data/exchange-rate?base=USD&target=EUR")
    assert response.status_code == 200
    assert response.json()["base_currency"] == "USD"
    
    # Test 404/500 handling logic inside route
    response = await client.get("/api/v1/market-data/exchange-rate?base=FAIL&target=EUR")
    assert response.status_code == 500

@pytest.mark.asyncio
async def test_get_earnings_calendar(client: AsyncClient):
    response = await client.get("/api/v1/market-data/earnings/AAPL")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_dividend_history(client: AsyncClient):
    response = await client.get("/api/v1/market-data/dividends/AAPL")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_stock_splits(client: AsyncClient):
    response = await client.get("/api/v1/market-data/splits/AAPL")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_market_indices(client: AsyncClient):
    response = await client.get("/api/v1/market-data/indices")
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_get_sector_industry(client: AsyncClient):
    response = await client.get("/api/v1/market-data/sector/AAPL")
    assert response.status_code == 200
    assert response.json()["symbol"] == "AAPL"
    
    response = await client.get("/api/v1/market-data/sector/UNKNOWN")
    assert response.status_code == 404
