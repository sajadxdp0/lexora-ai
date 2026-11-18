"""Cache service using Redis."""

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class CacheService:
    """
    Redis-based caching service.

    Features:
    - Async operations
    - JSON serialization
    - TTL support
    - Connection pooling

    Design decision: Use Redis for caching queries and responses.
    """

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Initialize Redis connection."""
        if self.redis is None:
            try:
                self.redis = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                # Test the connection
                await self.redis.ping()
                logger.info("redis_connected")
            except Exception as e:
                logger.warning("redis_connection_failed", error=str(e))
                self.redis = None

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None
            logger.info("redis_disconnected")

    async def _ensure_connected(self) -> None:
        """Lazily open the connection on first use."""
        if not self.redis:
            await self.connect()

    async def get(self, key: str) -> Optional[dict]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        await self._ensure_connected()

        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning("cache_get_error", key=key, error=str(e))

        return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expire: TTL in seconds

        Returns:
            True if successful
        """
        await self._ensure_connected()

        try:
            serialized = json.dumps(value)
            if expire:
                await self.redis.setex(key, expire, serialized)
            else:
                await self.redis.set(key, serialized)
            return True
        except Exception as e:
            logger.warning("cache_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        await self._ensure_connected()

        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.warning("cache_delete_error", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        await self._ensure_connected()

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.warning("cache_exists_error", key=key, error=str(e))
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache."""
        await self._ensure_connected()

        try:
            return await self.redis.incrby(key, amount)
        except Exception as e:
            logger.warning("cache_increment_error", key=key, error=str(e))
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set TTL on a key."""
        await self._ensure_connected()

        try:
            return await self.redis.expire(key, seconds)
        except Exception as e:
            logger.warning("cache_expire_error", key=key, error=str(e))
            return False

    async def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        await self._ensure_connected()

        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning("cache_flush_error", pattern=pattern, error=str(e))
            return 0


cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get cache service instance."""
    await cache_service.connect()
    return cache_service
