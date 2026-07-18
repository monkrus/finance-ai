"""Security tests: AI chat memory must be isolated per authenticated user.

Two users using the *same* client-supplied session id must not be able to
read or continue each other's conversation.
"""
import pytest
from fastapi.testclient import TestClient

from main import app
from app.api.deps import get_current_user
from app.schemas.user import UserProfileResponse
from app.ai.memory_manager import MemoryManager
from app.ai.models import AIMessage
import app.api.v1.ai as ai_mod
from app.api.v1.ai import scoped_session_id


def test_scoped_session_id_is_per_user():
    a = scoped_session_id(1, "shared")
    b = scoped_session_id(2, "shared")
    assert a != b
    assert "shared" in a and "shared" in b
    assert "1" in a and "2" in b


@pytest.mark.asyncio
async def test_memory_is_isolated_across_scoped_sessions():
    # A single manager (single backing store) — isolation must come from the key.
    manager = MemoryManager()
    s1 = scoped_session_id(1, "shared")
    s2 = scoped_session_id(2, "shared")
    await manager.clear_history(s1)
    await manager.clear_history(s2)

    await manager.add_message(s1, AIMessage(role="user", content="user-1 private note"))

    assert len(await manager.get_history(s1)) == 1
    # User 2's namespace must be empty even though the client session id matches.
    assert await manager.get_history(s2) == []


def test_chat_endpoint_namespaces_session_by_user():
    """Two different authenticated users posting the same session_id must reach
    two different memory namespaces at the router boundary."""
    captured = []

    async def fake_chat(session_id, message):
        captured.append(session_id)
        return "ok"

    original_chat = ai_mod.agent_router.chat
    ai_mod.agent_router.chat = fake_chat

    def override(user_id):
        async def _o():
            return UserProfileResponse(id=user_id, email=f"u{user_id}@example.com", is_active=True, is_verified=True)
        return _o

    try:
        client = TestClient(app)

        app.dependency_overrides[get_current_user] = override(1)
        r1 = client.post("/api/v1/ai/chat", json={"session_id": "shared", "message": "hi"})
        assert r1.status_code == 200

        app.dependency_overrides[get_current_user] = override(2)
        r2 = client.post("/api/v1/ai/chat", json={"session_id": "shared", "message": "hi"})
        assert r2.status_code == 200

        assert captured[0] != captured[1]
        assert captured[0] == scoped_session_id(1, "shared")
        assert captured[1] == scoped_session_id(2, "shared")
    finally:
        ai_mod.agent_router.chat = original_chat
        app.dependency_overrides.pop(get_current_user, None)
