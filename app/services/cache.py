import logging
import time
from typing import Any, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    A simple in-memory cache and rate limiter.
    Replaces Redis so the application can run standalone without external dependencies.
    """

    def __init__(self) -> None:
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.ttl = settings.cache_ttl_seconds

    async def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() < entry["expires_at"]:
                return entry["value"]
            else:
                del self.cache[key]
        return None

    async def set(self, key: str, value: Any) -> bool:
        self.cache[key] = {"value": value, "expires_at": time.time() + self.ttl}
        return True

    async def is_rate_limited(
        self, identifier: str, limit: int, window: int = 60
    ) -> bool:
        """Returns True if rate limited, False otherwise"""
        now = time.time()
        key = f"rate_limit:{identifier}"

        if (
            key not in self.rate_limits
            or self.rate_limits[key]["window_start"] < now - window
        ):
            self.rate_limits[key] = {"count": 1, "window_start": now}
            return False

        self.rate_limits[key]["count"] += 1
        return self.rate_limits[key]["count"] > limit


cache_service = CacheService()
