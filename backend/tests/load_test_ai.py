import pytest
import asyncio
from unittest.mock import AsyncMock
from app.ai.gateway import AIGatewayService
from app.ai.models import AIResponse

@pytest.mark.asyncio
async def test_concurrent_requests():
    service = AIGatewayService()
    
    async def mock_generate(*args, **kwargs):
        await asyncio.sleep(0.01) # Simulate network latency
        return AIResponse(content="Concurrent test")
        
    service.provider.generate_content = AsyncMock(side_effect=mock_generate)
    
    async def run_req(i):
        return await service.chat(f"session_conc_{i}", "Test input")
        
    results = await asyncio.gather(*[run_req(i) for i in range(50)])
    
    assert len(results) == 50
    assert all(r == "Concurrent test" for r in results)
