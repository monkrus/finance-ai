import logging
import json
from typing import List
from app.ai.models import AIMessage
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages conversational context and implements sliding window memory.
    """
    def __init__(self, max_tokens: int = 4000):
        from app.core.config import settings
        if settings.ENVIRONMENT == "test":
            import fakeredis.aioredis
            self.redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        else:
            self.redis = get_redis_client()
        self.max_tokens = max_tokens

    async def get_history(self, session_id: str) -> List[AIMessage]:
        key = f"ai:memory:{session_id}"
        raw_data = await self.redis.lrange(key, 0, -1)
        if not raw_data:
            return []
        
        messages = []
        for r in raw_data:
            data = json.loads(r)
            messages.append(AIMessage(**data))
        return messages

    async def add_message(self, session_id: str, message: AIMessage):
        key = f"ai:memory:{session_id}"
        await self.redis.rpush(key, message.model_dump_json())
        await self.redis.expire(key, 86400) # 24 hours TTL

    async def clear_history(self, session_id: str):
        key = f"ai:memory:{session_id}"
        await self.redis.delete(key)

    def _estimate_tokens(self, text: str) -> int:
        try:
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")
            return len(encoding.encode(text))
        except Exception:
            return max(1, len(text) // 4)

    async def compress_context_if_needed(self, session_id: str):
        key = f"ai:memory:{session_id}"
        messages = await self.get_history(session_id)
        if not messages:
            return
            
        total_tokens = sum(self._estimate_tokens(m.content) for m in messages)
        
        if total_tokens > self.max_tokens:
            logger.info(f"Compressing context for {session_id} (Tokens: {total_tokens}/{self.max_tokens})")
            keep_count = 0
            running_tokens = 0
            for m in reversed(messages):
                tokens = self._estimate_tokens(m.content)
                if running_tokens + tokens > self.max_tokens:
                    break
                running_tokens += tokens
                keep_count += 1
                
            if keep_count > 0:
                await self.redis.ltrim(key, -keep_count, -1)
            else:
                await self.redis.ltrim(key, -1, -1)
