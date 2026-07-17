import json
import logging
import hashlib
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

class NotificationQueue:
    def __init__(self):
        self.queue_key = "notifications:queue"
    
    def _generate_dedup_key(self, user_id: int, title: str, category: str) -> str:
        # Simple deduplication hashing
        key_str = f"{user_id}:{title}:{category}"
        return f"notifications:dedup:{hashlib.md5(key_str.encode()).hexdigest()}"

    async def enqueue(self, payload: dict, dedup_ttl_seconds: int = 3600) -> bool:
        """
        Pushes a notification event to the Redis queue for background processing.
        Returns False if duplicate (throttled).
        """
        redis = get_redis_client()
        user_id = payload.get("user_id")
        title = payload.get("title", "")
        category = payload.get("category", "system")
        
        if not user_id:
            logger.warning("Attempted to queue notification without user_id")
            return False

        # Deduplication check and enqueue
        dedup_key = self._generate_dedup_key(user_id, title, category)
        try:
            if await redis.get(dedup_key):
                logger.info(f"Notification suppressed by deduplication: {title} for user {user_id}")
                return False
                
            # Add to queue
            await redis.lpush(self.queue_key, json.dumps(payload))
            # Set deduplication lock
            await redis.setex(dedup_key, dedup_ttl_seconds, "1")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue notification: {e}")
            return False

    async def dequeue(self, batch_size: int = 50) -> list:
        """Pops a batch of messages from the Redis queue."""
        redis = get_redis_client()
        messages = []
        try:
            # We use basic rpop in a loop for simple batching. (Or pipeline)
            pipe = redis.pipeline()
            for _ in range(batch_size):
                pipe.rpop(self.queue_key)
            results = await pipe.execute()
            
            for res in results:
                if res:
                    messages.append(json.loads(res))
            return messages
        except Exception as e:
            logger.error(f"Failed to dequeue notifications: {e}")
            return []

    async def queue_length(self) -> int:
        redis = get_redis_client()
        try:
            return await redis.llen(self.queue_key)
        except Exception:
            return 0
