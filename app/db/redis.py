from functools import lru_cache
from typing import Optional

from aioredis import Redis

from db.base import AbstractCacheStorage

CACHE_EXPIRE_IN_SECONDS = 60

redis: Redis = None

# Функция понадобится при внедрении зависимостей
async def get_redis() -> Redis:
    return redis


class RedisStorage(AbstractCacheStorage):
    """Хранилище redis для кэша"""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str):
        return await self.redis.get(key=key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> None:
        if expire is None:
            expire = CACHE_EXPIRE_IN_SECONDS
        return await self.redis.set(key=key, value=value, expire=expire)


@lru_cache()
async def get_cache_storage() -> RedisStorage:
    redis = await get_redis()
    return RedisStorage(redis=redis)
