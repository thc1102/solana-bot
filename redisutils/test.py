import asyncio
import json
import pickle
import time
import redis.asyncio as redis

from solana_dex.model.pool import PoolInfo


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


async def get_keys_count(redis, pattern):
    count = 0
    cursor = b'0'  # 初始游标为 0

    while cursor:
        cursor, keys = await redis.scan(cursor, match=pattern, count=10000)
        count += len(keys)

    return count


async def test():
    r = await redis.from_url("redis://localhost")
    t = time.time()
    async with r.pipeline(transaction=True) as pipe:
        for key, value in (await get_data_list()).items():
            pipe.set(f"pool:{key}", pickle.dumps(value))
        await pipe.execute()
    print(time.time() - t)
    # t = time.time()
    # pool = await r.get("pool:ECGYvDxNhm3w482JGhGwviDkV7exJJey6ZvXK3kathFM")
    # if pool:
    #     print(pickle.loads(pool).__dict__)
    # print(time.time() - t)
    # t = time.time()
    # keys_count = await get_keys_count(r, "pool:*")
    # print(keys_count)
    # print(time.time() - t)


asyncio.run(test())
