import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.notifications.rules import RulesEngine
from app.notifications.queue import NotificationQueue
from app.notifications.delivery import NotificationService, EmailProvider, PushProvider, WebhookProvider, InAppProvider
from app.notifications.engine import NotificationEngine
from app.notifications.generators import AlertGenerator
from app.notifications.worker import NotificationWorker
from app.models.notification import Notification, NotificationPreference, NotificationRule
from app.schemas.notification import NotificationCreate
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timezone
import json

@pytest.fixture
def test_client():
    return TestClient(app)

def test_rules():
    e = RulesEngine()
    assert e.evaluate({"target": "x", "operator": ">", "value": 1}, {"x": 2}) == True
    assert e.evaluate({"target": "x", "operator": "==", "value": 1}, {"x": 1}) == True
    assert e.evaluate({"target": "x.y", "operator": ">", "value": 1}, {"x": {"y": 2}}) == True

@pytest.mark.asyncio
async def test_queue():
    q = NotificationQueue()
    with patch("app.notifications.queue.get_redis_client") as m:
        m.return_value = AsyncMock()
        m.return_value.get.return_value = None
        await q.enqueue({"user_id": 1, "title": "A", "category": "sys"})
        m.return_value.get.return_value = b"1"
        await q.enqueue({"user_id": 1, "title": "A", "category": "sys"})
        
        m.return_value.pipeline.return_value.execute.return_value = [json.dumps({"user_id": 1})]
        await q.dequeue()
        
        m.return_value.llen.return_value = 5
        await q.queue_length()

@pytest.mark.asyncio
async def test_delivery():
    db = AsyncMock()
    s = NotificationService(db)
    n = Notification(id=1, user_id=1, title="A")
    with patch.object(EmailProvider, "send", new_callable=AsyncMock) as me, \
         patch.object(PushProvider, "send", new_callable=AsyncMock) as mp, \
         patch.object(WebhookProvider, "send", new_callable=AsyncMock) as mw, \
         patch.object(InAppProvider, "send", new_callable=AsyncMock) as mia:
         me.return_value = True
         mp.return_value = True
         mw.return_value = True
         mia.return_value = True
         await s.deliver(n, ["email", "push", "webhook", "in_app"])

@pytest.mark.asyncio
async def test_engine():
    db = AsyncMock()
    e = NotificationEngine(db)
    
    # Patch queue to prevent Redis dependency
    with patch("app.notifications.queue.NotificationQueue.enqueue", new_callable=AsyncMock):
        # Manually create the Notification object to avoid Pydantic+AsyncMock issues
        mock_notification = Notification(id=1, user_id=1, title="A", message="B", category="system", priority="normal")
        
        # Patch the internals
        db.add = MagicMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock(side_effect=lambda obj: setattr(obj, 'id', 1))
        
        n = await e.create_notification(NotificationCreate(user_id=1, title="A", message="B", category="system", priority="normal"))
        assert n.title == "A"
        
    rule = NotificationRule(id=1, user_id=1, name="TestRule", condition_json={"target": "val", "operator": ">", "value": 1}, cooldown_minutes=0, is_active=True, priority="normal")
    
    class MockRes:
        def scalars(self):
            class S:
                def all(self): return [rule]
            return S()
    db.execute = AsyncMock(return_value=MockRes())
    with patch.object(NotificationEngine, "create_notification", new_callable=AsyncMock) as mc:
        await e.process_event(1, "cat", {"val": 2})
        assert mc.call_count == 1
        
    db.execute.return_value = AsyncMock(rowcount=1)
    await e.mark_as_read(1, 1)
    await e.archive(1, 1)
    await e.snooze(1, 1, datetime.now())

@pytest.mark.asyncio
async def test_generators():
    db = AsyncMock()
    gen = AlertGenerator(db)
    
    with patch("app.portfolio.engine.PortfolioEngine.get_user_portfolios_summary", new_callable=AsyncMock) as mp, \
         patch("app.market_data.service.MarketDataService.get_quote", new_callable=AsyncMock) as mm, \
         patch("app.news.engine.NewsIntelligenceEngine.get_recent_news", new_callable=AsyncMock) as mn, \
         patch("app.notifications.engine.NotificationEngine.create_notification", new_callable=AsyncMock) as mc:
         
         mp.return_value = {"daily_change_percent": -10.0}
         await gen.run_portfolio_checks(1)
         
         quote_mock = MagicMock()
         quote_mock.change_percent = 10.0
         mm.return_value = quote_mock
         await gen.run_market_checks(1, ["AAPL"])
         
         news_mock = MagicMock()
         news_mock.id = 1
         news_mock.headline = "Test"
         mn.return_value = [news_mock]
         await gen.run_news_checks(1)
         
         # run_wealth_checks now raises NotImplementedError (caught and logged)
         await gen.run_wealth_checks(1)
         
         # Only 3 notifications: portfolio, market, news. Wealth is NotImplementedError.
         assert mc.call_count == 3

@pytest.mark.asyncio
async def test_worker():
    w = NotificationWorker()
    with patch("app.notifications.queue.NotificationQueue.dequeue", new_callable=AsyncMock) as mdq, \
         patch("app.notifications.worker.AsyncSessionLocal") as mas, \
         patch("app.notifications.delivery.NotificationService.deliver", new_callable=AsyncMock) as mdel:
         
         mdq.return_value = [{"notification_id": 1, "category": "system", "user_id": 1}]
         
         db = AsyncMock()
         mas.return_value.__aenter__.return_value = db
         
         pref = NotificationPreference(user_id=1, email_enabled=True, push_enabled=True, in_app_enabled=True, category_preferences={})
         
         class MockRes:
             def __init__(self, v): self.v = v
             def scalar_one_or_none(self): return self.v
         
         n = Notification(id=1, user_id=1, category="system")
         db.execute = AsyncMock(side_effect=[MockRes(n), MockRes(pref)])
         
         await w.process_batch()
         assert mdel.call_count == 1

def test_api(test_client):
    from app.api.auth import get_current_user
    from app.models.user import User
    app.dependency_overrides[get_current_user] = lambda: User(id=1)
    
    with patch("app.notifications.engine.NotificationEngine.get_user_notifications", new_callable=AsyncMock) as mg, \
         patch("app.notifications.engine.NotificationEngine.create_notification", new_callable=AsyncMock) as mc, \
         patch("app.notifications.engine.NotificationEngine.archive", new_callable=AsyncMock) as ma, \
         patch("app.notifications.engine.NotificationEngine.mark_as_read", new_callable=AsyncMock) as mr:
         
         mg.return_value = []
         test_client.get("/api/v1/notifications")
         
         mc.return_value = Notification(id=1)
         test_client.post("/api/v1/notifications/test")
         
         ma.return_value = True
         test_client.post("/api/v1/notifications/archive/1")
         
         mr.return_value = True
         test_client.post("/api/v1/notifications/read/1")
    app.dependency_overrides.clear()
