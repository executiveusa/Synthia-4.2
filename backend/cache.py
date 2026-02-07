"""
Synthia 4.2 - Redis Cache Layer

Provides caching for skills, design tokens, and API responses
to improve performance. Falls back gracefully when Redis is unavailable.
"""

import json
import os
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Redis is optional — graceful degradation
try:
    import redis
    _redis_available = True
except ImportError:
    _redis_available = False


class CacheService:
    """Redis-backed cache with graceful fallback to in-memory dict."""

    def __init__(self):
        self._memory_cache: dict[str, str] = {}
        self._redis: Optional[Any] = None

        if _redis_available:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            try:
                self._redis = redis.from_url(redis_url, decode_responses=True)
                self._redis.ping()
                logger.info("Redis cache connected: %s", redis_url)
            except Exception as e:
                logger.warning("Redis unavailable, using in-memory cache: %s", e)
                self._redis = None

    @property
    def is_redis_connected(self) -> bool:
        return self._redis is not None

    def get(self, key: str) -> Optional[Any]:
        """Get a cached value. Returns None on miss."""
        try:
            if self._redis:
                data = self._redis.get(key)
            else:
                data = self._memory_cache.get(key)

            return json.loads(data) if data else None
        except Exception as e:
            logger.debug("Cache get error for '%s': %s", key, e)
            return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set a cached value with TTL in seconds (default 1 hour)."""
        try:
            serialized = json.dumps(value)
            if self._redis:
                self._redis.setex(key, ttl, serialized)
            else:
                self._memory_cache[key] = serialized
        except Exception as e:
            logger.debug("Cache set error for '%s': %s", key, e)

    def delete(self, key: str) -> None:
        """Delete a cached value."""
        try:
            if self._redis:
                self._redis.delete(key)
            else:
                self._memory_cache.pop(key, None)
        except Exception as e:
            logger.debug("Cache delete error for '%s': %s", key, e)

    def flush(self) -> None:
        """Clear all cached values."""
        try:
            if self._redis:
                self._redis.flushdb()
            else:
                self._memory_cache.clear()
        except Exception as e:
            logger.debug("Cache flush error: %s", e)


# Singleton
_cache: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Get or create the cache service singleton."""
    global _cache
    if _cache is None:
        _cache = CacheService()
    return _cache
