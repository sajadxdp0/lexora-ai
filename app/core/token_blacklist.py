"""Shared JWT revocation helpers backed by the Redis cache."""

from app.services.cache_service import get_cache_service

BLACKLIST_PREFIX = "token_blacklist:"


def blacklist_key(token_id: str) -> str:
    """Return the cache key used to mark a token id as revoked."""
    return f"{BLACKLIST_PREFIX}{token_id}"


async def is_token_blacklisted(token_id: str | None) -> bool:
    """Return whether a token id has been revoked."""
    if not token_id:
        return False
    cache = await get_cache_service()
    return await cache.exists(blacklist_key(token_id))


async def blacklist_token(
    token_id: str | None,
    ttl_seconds: int,
    **extra: object,
) -> bool:
    """Revoke a token id for its remaining lifetime; return whether it was stored.

    A missing id or a non-positive TTL is a no-op, matching the previous
    per-endpoint guards that skipped cache writes in those cases.
    """
    if not token_id or ttl_seconds <= 0:
        return False
    cache = await get_cache_service()
    return await cache.set(
        blacklist_key(token_id),
        {"revoked": True, **extra},
        expire=ttl_seconds,
    )
