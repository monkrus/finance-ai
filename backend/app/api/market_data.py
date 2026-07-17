from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from app.market_data.service import MarketDataService
from app.market_data.models import (
    CompanyProfile,
    StockQuote,
    HistoricalPriceSeries,
    IncomeStatement,
    BalanceSheet,
    CashFlowStatement,
    CompanySearchResult, FinancialRatios, MarketNews,
    EconomicIndicator, ExchangeRate, EarningsEvent,
    DividendHistory, StockSplit, MarketIndex, SectorIndustryClass
)

router = APIRouter()

def get_market_data_service() -> MarketDataService:
    return MarketDataService()

@router.get("/profile/{ticker}", response_model=CompanyProfile, summary="Get Company Profile")
async def get_company_profile(ticker: str, service: MarketDataService = Depends(get_market_data_service)):
    """Fetch the company profile including sector, industry, and description."""
    result = await service.get_company_profile(ticker)
    if not result:
        raise HTTPException(status_code=404, detail=f"Company profile for {ticker} not found.")
    return result

@router.get("/quote/{ticker}", response_model=StockQuote, summary="Get Real-time Quote")
async def get_stock_quote(ticker: str, service: MarketDataService = Depends(get_market_data_service)):
    """Fetch real-time stock quote and daily ranges."""
    result = await service.get_quote(ticker)
    if not result:
        raise HTTPException(status_code=404, detail=f"Quote for {ticker} not found.")
    return result

@router.get("/historical/{ticker}", response_model=HistoricalPriceSeries, summary="Get Historical Prices")
async def get_historical_prices(
    ticker: str,
    from_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    to_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    service: MarketDataService = Depends(get_market_data_service)
):
    """Fetch end-of-day historical prices for a given ticker."""
    result = await service.get_historical_prices(ticker, from_date, to_date)
    if not result:
        raise HTTPException(status_code=404, detail=f"Historical data for {ticker} not found.")
    return result

@router.get("/financials/{ticker}/income", response_model=List[IncomeStatement], summary="Get Income Statements")
async def get_income_statements(
    ticker: str,
    limit: int = Query(4, ge=1, le=10, description="Number of periods to return"),
    period: str = Query("annual", description="Period type: 'annual' or 'quarter'"),
    service: MarketDataService = Depends(get_market_data_service)
):
    """Fetch historical income statements."""
    result = await service.get_income_statements(ticker, limit, period)
    if not result:
        raise HTTPException(status_code=404, detail=f"Income statements for {ticker} not found.")
    return result

@router.get("/financials/{ticker}/balance-sheet", response_model=List[BalanceSheet], summary="Get Balance Sheets")
async def get_balance_sheets(
    ticker: str,
    limit: int = Query(4, ge=1, le=10, description="Number of periods to return"),
    period: str = Query("annual", description="Period type: 'annual' or 'quarter'"),
    service: MarketDataService = Depends(get_market_data_service)
):
    """Fetch historical balance sheets."""
    result = await service.get_balance_sheets(ticker, limit, period)
    if not result:
        raise HTTPException(status_code=404, detail=f"Balance sheets for {ticker} not found.")
    return result

@router.get("/financials/{ticker}/cash-flow", response_model=List[CashFlowStatement], summary="Get Cash Flow Statements")
async def get_cash_flow_statements(
    ticker: str,
    limit: int = Query(4, ge=1, le=10, description="Number of periods to return"),
    period: str = Query("annual", description="Period type: 'annual' or 'quarter'"),
    service: MarketDataService = Depends(get_market_data_service)
):
    """Fetch historical cash flow statements."""
    result = await service.get_cash_flow_statements(ticker, limit, period)
    if not result:
        raise HTTPException(status_code=404, detail=f"Cash flow statements for {ticker} not found.")
    return result

@router.get("/search", response_model=List[CompanySearchResult], summary="Search Company")
async def search_company(query: str, service: MarketDataService = Depends(get_market_data_service)):
    return await service.search_company(query)

@router.get("/ratios/{ticker}", response_model=List[FinancialRatios], summary="Get Financial Ratios")
async def get_financial_ratios(ticker: str, service: MarketDataService = Depends(get_market_data_service)):
    return await service.get_financial_ratios(ticker)

@router.get("/news/{ticker}", response_model=List[MarketNews], summary="Get Market News")
async def get_market_news(ticker: str, limit: int = 10, service: MarketDataService = Depends(get_market_data_service)):
    return await service.get_market_news(ticker, limit)

@router.get("/economic/{indicator}", response_model=List[EconomicIndicator], summary="Get Economic Indicator")
async def get_economic_indicator(indicator: str, service: MarketDataService = Depends(get_market_data_service)):
    return await service.get_economic_indicator(indicator)

@router.get("/exchange-rate", response_model=ExchangeRate, summary="Get Exchange Rate")
async def get_exchange_rate(base: str, target: str, service: MarketDataService = Depends(get_market_data_service)):
    result = await service.get_exchange_rate(base, target)
    if not result:
        raise HTTPException(status_code=404, detail="Exchange rate not found.")
    return result

@router.get("/earnings/{ticker}", response_model=List[EarningsEvent], summary="Get Earnings Calendar")
async def get_earnings_calendar(ticker: str, service: MarketDataService = Depends(get_market_data_service)):
    return await service.get_earnings_calendar(ticker)

@router.get("/dividends/{ticker}", response_model=List[DividendHistory], summary="Get Dividend History")
async def get_dividend_history(ticker: str, service: MarketDataService = Depends(get_market_data_service)):
    return await service.get_dividend_history(ticker)

@router.get("/splits/{ticker}", response_model=List[StockSplit], summary="Get Stock Splits")
async def get_stock_splits(ticker: str, service: MarketDataService = Depends(get_market_data_service)):
    return await service.get_stock_splits(ticker)

@router.get("/indices", response_model=List[MarketIndex], summary="Get Market Indices")
async def get_market_indices(service: MarketDataService = Depends(get_market_data_service)):
    return await service.get_market_indices()

@router.get("/sector/{ticker}", response_model=SectorIndustryClass, summary="Get Sector and Industry")
async def get_sector_industry(ticker: str, service: MarketDataService = Depends(get_market_data_service)):
    result = await service.get_sector_industry(ticker)
    if not result:
        raise HTTPException(status_code=404, detail="Sector classification not found.")
    return result
