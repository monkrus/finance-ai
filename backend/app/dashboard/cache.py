import json
import logging
import hashlib
from typing import Any, Callable, Optional, TypeVar
from functools import wraps
from pydantic import BaseModel
from app.core.redis import get_redis_client

logger = logging.getLogger(__name__)

T = TypeVar('T')

class DashboardCache:
    """Intelligent Redis caching for Dashboard orchestration."""
    
    @staticmethod
    def _generate_key(func_name: str, args: tuple, kwargs: dict) -> str:
        key_str = f"{func_name}:{args}:{kwargs}"
        return f"dashboard:cache:{hashlib.md5(key_str.encode()).hexdigest()}"

    @classmethod
    def cached(cls, ttl_seconds: int = 60, bypass_cache: bool = False):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                if bypass_cache:
                    return await func(*args, **kwargs)

                redis = get_redis_client()
                cache_key = cls._generate_key(func.__name__, args, kwargs)
                
                try:
                    cached_data = await redis.get(cache_key)
                    if cached_data:
                        logger.debug(f"Cache hit for {cache_key}")
                        return json.loads(cached_data)
                except Exception as e:
                    logger.warning(f"Redis cache read error: {str(e)}. Proceeding without cache.")
                
                # Cache miss or read error
                result = await func(*args, **kwargs)
                
                # Serialize Pydantic objects if necessary
                cache_payload = result
                if isinstance(result, BaseModel):
                    cache_payload = result.model_dump(mode="json")
                elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], BaseModel):
                    cache_payload = [item.model_dump(mode="json") for item in result]
                elif isinstance(result, dict):
                    # basic sanitization, assume simple dict
                    pass
                
                try:
                    await redis.setex(cache_key, ttl_seconds, json.dumps(cache_payload))
                except Exception as e:
                    logger.warning(f"Redis cache write error: {str(e)}.")
                    
                return result
            return wrapper
        return decorator

    @classmethod
    async def invalidate(cls, func_name: str, args: tuple, kwargs: dict):
        redis = get_redis_client()
        cache_key = cls._generate_key(func_name, args, kwargs)
        await redis.delete(cache_key)
