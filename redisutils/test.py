import asyncio
import json
import time
import redis.asyncio as redis


class PoolInfo:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.baseMint = data.get("baseMint")
        self.quoteMint = data.get("quoteMint")
        self.authority = data.get("authority")
        self.openOrders = data.get("openOrders")
        self.targetOrders = data.get("targetOrders")
        self.baseVault = data.get("baseVault")
        self.quoteVault = data.get("quoteVault")
        self.marketId = data.get("marketId")
        self.marketBids = data.get("marketBids")
        self.marketAsks = data.get("marketAsks")
        self.marketBaseVault = data.get("marketBaseVault")
        self.marketQuoteVault = data.get("marketQuoteVault")
        self.marketAuthority = data.get("marketAuthority")
        self.marketEventQueue = data.get("marketEventQueue")


async def get_data_list():
    pool_data = {}
    data_list = []
    with open(r"D:\Code\Python\solana-bot\liquidity_mainnet.json", encoding="utf8") as f:
        data_json = json.loads(f.read())
    data_list.extend(data_json.get("unOfficial"))
    filtered_list = [item for item in data_list if
                     item.get("quoteMint") == "So11111111111111111111111111111111111111112"]
    for data in filtered_list:
        pool = PoolInfo(data)
        pool_data[pool.baseMint] = pool
    return pool_data


async def write_to_redis(redis, data):
    async with redis.pipeline(transaction=True) as pipe:
        for key, value in data.items():
            pipe.set(key, value)
        return await pipe.execute()


async def test():
    r = await redis.from_url("redis://localhost")
    t = time.time()
    async with r.pipeline(transaction=True) as pipe:
        for key, value in (await get_data_list()).items():
            pipe.set(f"pool:{key}", json.dumps(value.__dict__))
        await pipe.execute()
    print(time.time() - t)
    t = time.time()
    print(await r.get("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"))
    print(time.time() - t)


asyncio.run(test())
