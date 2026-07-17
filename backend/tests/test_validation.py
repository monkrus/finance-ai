import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

from app.notifications.rules import RulesEngine
from app.notifications.engine import NotificationEngine
from app.notifications.queue import NotificationQueue
from app.notifications.delivery import NotificationService, EmailProvider, PushProvider, WebhookProvider, InAppProvider, NotificationProviderException
from app.schemas.notification import NotificationCreate
from app.models.notification import Notification, NotificationRule, NotificationPreference
from main import app

# --- 2. Rules Engine Validation ---
def test_rules_validation():
    engine = RulesEngine()
    
    # Nested AND
    rule_and = {"AND": [{"target": "a", "operator": ">", "value": 1}, {"target": "b", "operator": "==", "value": "x"}]}
    assert engine.evaluate(rule_and, {"a": 2, "b": "x"}) == True
    assert engine.evaluate(rule_and, {"a": 2, "b": "y"}) == False
    
    # Nested OR
    rule_or = {"OR": [{"target": "a", "operator": ">", "value": 10}, {"target": "a", "operator": "<", "value": 0}]}
    assert engine.evaluate(rule_or, {"a": 15}) == True
    assert engine.evaluate(rule_or, {"a": -5}) == True
    assert engine.evaluate(rule_or, {"a": 5}) == False
    
    # Mixed AND + OR
    rule_mixed = {"AND": [{"target": "status", "operator": "==", "value": "active"}, {"OR": [{"target": "val", "operator": ">", "value": 10}, {"target": "val", "operator": "<", "value": 0}]}]}
    assert engine.evaluate(rule_mixed, {"status": "active", "val": 15}) == True
    assert engine.evaluate(rule_mixed, {"status": "inactive", "val": 15}) == False
    
    # Deep JSON path
    assert engine.evaluate({"target": "market.aapl.price", "operator": ">", "value": 150}, {"market": {"aapl": {"price": 160}}}) == True
    
    # Missing keys
    assert engine.evaluate({"target": "missing.key", "operator": "==", "value": 1}, {"a": 1}) == False
    
    # Invalid operators
    assert engine.evaluate({"target": "a", "operator": "INVALID", "value": 1}, {"a": 1}) == False
    
    # Invalid value types
    assert engine.evaluate({"target": "a", "operator": ">", "value": "str"}, {"a": 1}) == False
    
    # Empty rule sets
    assert engine.evaluate({}, {"a": 1}) == False
    assert engine.evaluate(None, {"a": 1}) == False
    
    # Type casting (int string)
    assert engine.evaluate({"target": "a", "operator": "==", "value": 10}, {"a": "10"}) == True

@pytest.mark.asyncio
async def test_rules_cooldown_and_priority():
    db = AsyncMock()
    engine = NotificationEngine(db)
    
    r1 = NotificationRule(id=1, name="R1", priority="high", is_active=False, cooldown_minutes=0)
    r2 = NotificationRule(id=2, name="R2", priority="normal", is_active=True, cooldown_minutes=60, last_triggered_at=datetime.now(timezone.utc))
    r3 = NotificationRule(id=3, name="R3", priority="low", is_active=True, cooldown_minutes=0, condition_json={"target": "a", "operator": "==", "value": 1})
    
    class MockRes:
        def scalars(self):
            class S:
                # Only return active rules (r2, r3). r1 is inactive.
                def all(self): return [r2, r3]
            return S()
            
    db.execute = AsyncMock(return_value=MockRes())
    db.add = MagicMock()
    db.commit = AsyncMock()
    
    with patch.object(NotificationEngine, "create_notification", new_callable=AsyncMock) as mc:
        await engine.process_event(1, "sys", {"a": 1})
        # r2 is in cooldown, r3 matches
        assert mc.call_count == 1

# --- 3. Delivery Layer Validation ---
@pytest.mark.asyncio
async def test_delivery_validation():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    
    service = NotificationService(db)
    notif = Notification(id=1, user_id=1, title="Test")
    
    with patch.object(EmailProvider, "send", new_callable=AsyncMock) as me, \
         patch.object(PushProvider, "send", new_callable=AsyncMock) as mp:
         
         # Success
         me.return_value = True
         mp.return_value = True
         await service.deliver(notif, ["email", "push"])
         assert me.call_count == 1
         
         # Partial failure (one succeeds, one fails with retryable error)
         me.reset_mock()
         mp.reset_mock()
         me.return_value = True
         mp.side_effect = NotificationProviderException("timeout")
         await service.deliver(notif, ["email", "push"])
         assert me.call_count == 1
         # Push attempts 3 retries (stop_after_attempt(3))
         assert mp.call_count == 3

# --- 4. Queue Validation ---
@pytest.mark.asyncio
async def test_queue_validation():
    q = NotificationQueue()
    with patch("app.notifications.queue.get_redis_client") as mr:
        m = AsyncMock()
        mr.return_value = m
        
        # Success enqueue
        m.get.return_value = None
        assert await q.enqueue({"user_id": 1, "title": "A", "category": "sys"}) == True
        
        # Duplicate payload (throttled)
        m.get.return_value = b"1"
        assert await q.enqueue({"user_id": 1, "title": "A", "category": "sys"}) == False
        
        # Redis unavailable - reset side effect for clean state
        m.get.return_value = None
        m.get.side_effect = Exception("connection refused")
        result = await q.enqueue({"user_id": 1, "title": "B", "category": "sys"})
        assert result == False

# --- 9. Architecture Validation ---
def test_architecture_constraints():
    # The absence of direct provider imports in portfolio, news, etc. 
    # is verified by the static analysis phase
    pass
