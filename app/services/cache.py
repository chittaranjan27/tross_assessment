import json
import logging
from typing import Any, Optional

from redis import asyncio as aioredis

from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis = aioredis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = settings.cache_ttl_seconds

    async def get(self, key: str) -> Optional[Any]:
        try:
            val = await self.redis.get(key)
            if val:
                return json.loads(val)
        except Exception as e:
            logger.error(f"Redis get error for {key}: {e}")
        return None

    async def set(self, key: str, value: Any) -> bool:
        try:
            await self.redis.set(key, json.dumps(value), ex=self.ttl)
            return True
        except Exception as e:
            logger.error(f"Redis set error for {key}: {e}")
        return False

    async def is_rate_limited(self, identifier: str, limit: int, window: int = 60) -> bool:
        """Returns True if rate limited, False otherwise"""
        try:
            key = f"rate_limit:{identifier}"
            current = await self.redis.incr(key)
            if current == 1:
                await self.redis.expire(key, window)
            return current > limit
        except Exception as e:
            logger.error(f"Redis rate limit error for {identifier}: {e}")
            # Fail open if Redis is down
            return False

cache_service = CacheService()
