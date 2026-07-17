import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.dashboard.cache import DashboardCache
import json

@pytest.mark.asyncio
async def test_dashboard_cache_hit_and_miss():
    mock_redis = AsyncMock()
    # First call simulates a cache miss (returns None)
    # Second call simulates a cache hit (returns cached data)
    mock_redis.get.side_effect = [None, json.dumps({"cached": True})]
    
    with patch("app.dashboard.cache.get_redis_client", return_value=mock_redis):
        # We need a dummy function to cache
        call_count = 0
        
        @DashboardCache.cached(ttl_seconds=60)
        async def dummy_func(x):
            nonlocal call_count
            call_count += 1
            return {"cached": False, "val": x}
            
        # Call 1: Cache Miss
        res1 = await dummy_func(1)
        assert res1["cached"] is False
        assert call_count == 1
        assert mock_redis.setex.called
        
        # Call 2: Cache Hit
        res2 = await dummy_func(1)
        assert res2["cached"] is True
        assert call_count == 1 # Underlying function shouldn't be called again
        
@pytest.mark.asyncio
async def test_dashboard_cache_bypass():
    mock_redis = AsyncMock()
    with patch("app.dashboard.cache.get_redis_client", return_value=mock_redis):
        call_count = 0
        
        @DashboardCache.cached(ttl_seconds=60, bypass_cache=True)
        async def dummy_func(x):
            nonlocal call_count
            call_count += 1
            return {"val": x}
            
        res1 = await dummy_func(1)
        res2 = await dummy_func(1)
        
        assert call_count == 2
        assert not mock_redis.get.called
