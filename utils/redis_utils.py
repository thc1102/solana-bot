import asyncio
from typing import Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from settings.config import AppConfig


class RedisFactory:
    # redis 连接池
    _pool = redis.ConnectionPool.from_url(AppConfig.REDIS_URL)

    def __init__(self):
        self._pool = self.__class__._pool
        self._redis: Optional[Redis] = None

    @property
    def pool(self):
        return self._pool

    async def __aenter__(self) -> Redis:
        self._redis = redis.Redis.from_pool(self._pool)
        return self._redis

    async def __aexit__(self, exc_type, exc, tb):
        # 由于是共用连接池 所以不需要断开链接
        # return await self._redis.aclose()
        return
