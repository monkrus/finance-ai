import json
from typing import Optional, Any, Type, TypeVar, List
from pydantic import BaseModel, TypeAdapter
from app.core.redis import get_redis_client

T = TypeVar('T', bound=BaseModel)

class MarketDataCache:
    """
    Centralized Redis caching logic for Market Data Layer.
    Handles Pydantic serialization and dynamic TTLs.
    """
    def __init__(self):
        # We assume the redis client is already configured globally
        self.redis = get_redis_client()

    async def get(self, key: str, model: Type[T]) -> Optional[T]:
        """Fetch and deserialize a single Pydantic model from cache."""
        data = await self.redis.get(key)
        if data:
            try:
                # Redis client configured with decode_responses=True returns string
                return model.model_validate_json(data)
            except Exception:
                return None
        return None

    async def set(self, key: str, instance: T, ttl: int):
        """Serialize and set a single Pydantic model to cache with TTL (seconds)."""
        if instance is not None:
            await self.redis.set(key, instance.model_dump_json(), ex=ttl)

    async def get_list(self, key: str, model: Type[T]) -> Optional[List[T]]:
        """Fetch and deserialize a list of Pydantic models from cache."""
        data = await self.redis.get(key)
        if data:
            try:
                adapter = TypeAdapter(List[model])
                return adapter.validate_json(data)
            except Exception:
                return None
        return None

    async def set_list(self, key: str, instances: List[T], ttl: int):
        """Serialize and set a list of Pydantic models to cache with TTL (seconds)."""
        if instances is not None:
            adapter = TypeAdapter(List[type(instances[0]) if instances else Any])
            await self.redis.set(key, adapter.dump_json(instances).decode('utf-8'), ex=ttl)
