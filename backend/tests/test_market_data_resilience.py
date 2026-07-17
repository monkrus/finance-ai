import pytest
from unittest.mock import patch, AsyncMock
from app.market_data.service import MarketDataService
from app.core.exceptions import FinPilotException
from app.market_data.adapters.fmp_adapter import FMPAdapter
from app.market_data.adapters.finnhub_adapter import FinnhubAdapter
from app.market_data.adapters.alphavantage_adapter import AlphaVantageAdapter

@pytest.mark.asyncio
async def test_resilience_circuit_breaker():
    """Test that the service correctly falls back to secondary providers when primary fails."""
    service = MarketDataService()
    service.fmp = FMPAdapter(api_key="test")
    service.finnhub = FinnhubAdapter(api_key="test")
    service.alpha_vantage = AlphaVantageAdapter(api_key="test")
    
    # 1. Total Failure (All providers fail)
    with patch.object(service.fmp, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=500, message="FMP Down")), \
         patch.object(service.finnhub, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=502, message="Finnhub Down")), \
         patch.object(service.alpha_vantage, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=504, message="AV Timeout")), \
         patch.object(service.mock, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=500, message="Mock Down")):
        
        with pytest.raises(FinPilotException) as exc:
            await service.get_company_profile("RESILIENCE_TEST")
        
        # Should raise the LAST exception encountered
        assert exc.value.status_code == 500
        assert exc.value.message == "Mock Down"

    # 2. Partial Failure (Primary fails, Secondary succeeds)
    with patch.object(service.fmp, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=500, message="FMP Down")), \
         patch.object(service.finnhub, 'get_company_profile', new_callable=AsyncMock, side_effect=FinPilotException(status_code=502, message="Finnhub Down")):
        
        # It should fall back to Alpha Vantage, which we won't mock, so it returns MockAdapter behavior
        # (Since api keys aren't set, alpha_vantage is just mock adapter)
        profile = await service.get_company_profile("RESILIENCE_TEST_2")
        assert profile is not None
        assert profile.ticker == "RESILIENCE_TEST_2"

    # 3. Cache behavior during failure
    # If cache exists, it shouldn't even call the providers
    await service.cache.redis.set("md:profile:CACHED", '{"ticker": "CACHED", "company_name": "Cache Inc."}')
    
    with patch.object(service, '_fetch', new_callable=AsyncMock, side_effect=Exception("Should not be called!")):
        profile = await service.get_company_profile("CACHED")
        assert profile.ticker == "CACHED"
