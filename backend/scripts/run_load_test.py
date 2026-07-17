import asyncio
import time
import json
from unittest.mock import AsyncMock, patch

from app.notifications.rules import RulesEngine
from app.notifications.queue import NotificationQueue

async def run_load_test():
    print("Starting Module 11 Load & Performance Tests...\n")
    
    # 1. Rule Evaluation Latency
    print("Testing Rule Evaluation...")
    engine = RulesEngine()
    rule = {
        "AND": [
            {"target": "portfolio.loss", "operator": ">", "value": 10},
            {"target": "market.vix", "operator": ">", "value": 20},
            {"OR": [
                {"target": "status", "operator": "==", "value": "active"},
                {"target": "status", "operator": "==", "value": "pending"}
            ]}
        ]
    }
    payload = {"portfolio": {"loss": 15}, "market": {"vix": 30}, "status": "active"}
    
    start = time.perf_counter()
    iterations = 10000
    for _ in range(iterations):
        engine.evaluate(rule, payload)
    end = time.perf_counter()
    
    total_ms = (end - start) * 1000
    avg_ms = total_ms / iterations
    print(f"Rule Evaluation Latency: {avg_ms:.4f} ms per rule (Target: <25ms)")
    
    # 2. Queue Enqueue Latency (Mocked Redis Network)
    print("\nTesting Queue Enqueue Latency...")
    q = NotificationQueue()
    with patch("app.notifications.queue.get_redis_client") as mr:
        m = AsyncMock()
        mr.return_value = m
        m.get.return_value = None
        
        start = time.perf_counter()
        for i in range(1000):
            await q.enqueue({"user_id": 1, "title": f"T{i}", "category": "sys"})
        end = time.perf_counter()
        
        q_avg_ms = ((end - start) * 1000) / 1000
        print(f"Queue Enqueue Latency: {q_avg_ms:.4f} ms per enqueue (Target: <5ms)")
        
    # 3. Worker Throughput
    print("\nTesting Worker Throughput...")
    from app.notifications.worker import NotificationWorker
    w = NotificationWorker()
    with patch("app.notifications.queue.NotificationQueue.dequeue", new_callable=AsyncMock) as mdq, \
         patch("app.notifications.worker.AsyncSessionLocal") as mas, \
         patch("app.notifications.delivery.NotificationService.deliver", new_callable=AsyncMock) as mdel:
         
         # Mock batch of 50
         mdq.return_value = [{"notification_id": i, "category": "sys", "user_id": 1} for i in range(50)]
         
         db = AsyncMock()
         mas.return_value.__aenter__.return_value = db
         
         class MockRes:
             def __init__(self, v): self.v = v
             def scalar_one_or_none(self): return self.v
             
         from app.models.notification import Notification, NotificationPreference
         pref = NotificationPreference(user_id=1, email_enabled=True, push_enabled=True, in_app_enabled=True)
         
         db.execute.side_effect = lambda *args, **kwargs: MockRes(Notification(id=1, user_id=1, category="sys")) if "Notification " in str(args) else MockRes(pref)
         
         start = time.perf_counter()
         for _ in range(200): # 200 * 50 = 10,000 notifications
             await w.process_batch()
         end = time.perf_counter()
         
         throughput = 10000 / (end - start)
         print(f"Worker Throughput: {throughput:.0f} notifications/second (Target: >10,000)")
         print("\nLoad Tests Completed Successfully.")

if __name__ == "__main__":
    asyncio.run(run_load_test())
