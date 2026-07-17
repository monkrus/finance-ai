import pytest
import json
from app.ai.memory_manager import MemoryManager
from app.ai.models import AIMessage

@pytest.mark.asyncio
async def test_memory_add_and_get():
    manager = MemoryManager()
    await manager.clear_history("session_mem1")
    
    msg = AIMessage(role="user", content="Testing memory")
    await manager.add_message("session_mem1", msg)
    
    history = await manager.get_history("session_mem1")
    assert len(history) == 1
    assert history[0].role == "user"
    assert history[0].content == "Testing memory"

@pytest.mark.asyncio
async def test_memory_compression():
    # Force max_tokens very small so compression triggers
    manager = MemoryManager(max_tokens=20)
    await manager.clear_history("session_compress")
    
    # Add 25 messages. Each takes roughly 2 tokens ("Msg", " i")
    for i in range(25):
        msg = AIMessage(role="user", content=f"Msg {i}")
        await manager.add_message("session_compress", msg)
        
    # Compress
    await manager.compress_context_if_needed("session_compress")
    
    history = await manager.get_history("session_compress")
    
    assert len(history) < 25
    assert history[-1].content == "Msg 24"

@pytest.mark.asyncio
async def test_memory_compression_fallback():
    manager = MemoryManager(max_tokens=20)
    await manager.clear_history("session_fallback")
    
    # Force tiktoken to fail by patching sys.modules or just mock _estimate_tokens
    from unittest.mock import patch
    with patch.dict("sys.modules", {"tiktoken": None}):
        for i in range(25):
            msg = AIMessage(role="user", content=f"Msg {i}")
            await manager.add_message("session_fallback", msg)
            
        await manager.compress_context_if_needed("session_fallback")
        history = await manager.get_history("session_fallback")
        assert len(history) < 25
