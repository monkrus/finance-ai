import redis.asyncio as redis
from app.core.config import settings

redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=10,
    decode_responses=True
)

def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)
