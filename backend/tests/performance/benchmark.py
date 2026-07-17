import asyncio
import time
import os
import sys

# Add parent dir to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.market_data.service import MarketDataService

async def run_benchmark():
    service = MarketDataService()
    
    print("Starting Performance Benchmark...")
    print("-" * 50)
    
    # 1. Profile Retrieval (Cache Miss)
    start = time.time()
    await service.get_company_profile("AAPL")
    time_miss = time.time() - start
    print(f"Profile (Cache Miss): {time_miss:.4f}s")
    
    # 2. Profile Retrieval (Cache Hit)
    start = time.time()
    await service.get_company_profile("AAPL")
    time_hit = time.time() - start
    print(f"Profile (Cache Hit) : {time_hit:.4f}s")
    
    # 3. Batch Requests
    start = time.time()
    tasks = [service.get_quote("AAPL") for _ in range(50)]
    await asyncio.gather(*tasks)
    time_batch = time.time() - start
    print(f"Batch 50 Quotes     : {time_batch:.4f}s")
    
    print("-" * 50)
    print("Benchmark Complete.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
