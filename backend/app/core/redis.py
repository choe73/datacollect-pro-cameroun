"""Redis client configuration."""

import json
from typing import Any, Optional, Union
import redis.asyncio as aioredis

from app.core.config import settings

# Redis client instance
redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


class RedisCache:
    """Redis cache helper class."""
    
    def __init__(self, client: aioredis.Redis):
        self.client = client
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 3600,
        db: int = 0
    ) -> bool:
        """Set value in cache."""
        try:
            # Select database
            await self.client.execute_command("SELECT", db)
            serialized = json.dumps(value) if not isinstance(value, (str, bytes)) else value
            await self.client.setex(key, expire, serialized)
            return True
        except Exception:
            return False
    
    async def delete(self, key: str, db: int = 0) -> int:
        """Delete key from cache."""
        await self.client.execute_command("SELECT", db)
        return await self.client.delete(key)
    
    async def exists(self, key: str, db: int = 0) -> int:
        """Check if key exists."""
        await self.client.execute_command("SELECT", db)
        return await self.client.exists(key)
    
    async def ping(self) -> bool:
        """Check Redis connection."""
        try:
            await self.client.ping()
            return True
        except Exception:
            return False
    
    async def close(self):
        """Close Redis connection."""
        await self.client.close()


# Global cache instance
cache = RedisCache(redis_client)


# Database-specific cache helpers
async def get_cache(key: str, db: int = 0) -> Optional[Any]:
    """Get from specific Redis DB."""
    return await cache.get(key)


async def set_cache(key: str, value: Any, expire: int = 3600, db: int = 0) -> bool:
    """Set in specific Redis DB."""
    return await cache.set(key, value, expire, db)


async def delete_cache(key: str, db: int = 0) -> int:
    """Delete from specific Redis DB."""
    return await cache.delete(key, db)
