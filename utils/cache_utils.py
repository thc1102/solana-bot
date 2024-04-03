import asyncio
import time


class MyAsyncCache:
    def __init__(self, ttl=60, maxsize=300):
        self.cache = {}
        self.ttl = ttl
        self.maxsize = maxsize

    async def set(self, key, value):
        if len(self.cache) >= self.maxsize:
            await self.pop_earliest()
        self.cache[key] = (value, time.time())

    async def pop_earliest(self):
        earliest_key = None
        earliest_time = float('inf')
        for key, (_, timestamp) in self.cache.items():
            if timestamp < earliest_time:
                earliest_key = key
                earliest_time = timestamp
        if earliest_key:
            del self.cache[earliest_key]

    async def pop_earliest_not_expired(self):
        now = time.time()
        for key, (value, timestamp) in list(self.cache.items()):
            if timestamp + self.ttl >= now:
                del self.cache[key]
                return value
        return None


# 示例用法
async def main():
    cache = MyAsyncCache(ttl=60, maxsize=300)

    # 添加一些值到缓存
    await cache.set('key1', 'value1')
    await cache.set('key2', 'value2')
    await cache.set('key3', 'value3')

    await asyncio.sleep(100)

    # 弹出最早的未过期值
    earliest_value = await cache.pop_earliest_not_expired()
    print("弹出的值:", earliest_value)

    # 添加新值
    await cache.set('key4', 'value4')

    # 再次弹出最早的未过期值
    earliest_value = await cache.pop_earliest_not_expired()
    print("弹出的值:", earliest_value)


# 运行示例
asyncio.run(main())
