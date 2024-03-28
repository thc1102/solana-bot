import asyncio
import json
import pickle
import time

import httpx
import redis.asyncio as redis

from solana_dex.model.pool import PoolInfo


async def get_pool_list():
    pool_data = {}
    data_list = []
    with open(r"liquidity_mainnet.json", encoding="utf8") as f:
        data_json = json.loads(f.read())
    data_list.extend(data_json.get("unOfficial"))
    filtered_list = [item for item in data_list if
                     item.get("quoteMint") == "So11111111111111111111111111111111111111112"]
    for data in filtered_list:
        pool = PoolInfo(data)
        pool_data[pool.baseMint] = pool
    return pool_data


def download_file(url, filename):
    with httpx.stream("GET", url, proxies="http://127.0.0.1:10809") as response:
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            print("文件下载成功！")
            return True
        else:
            print("文件下载失败:", response.status_code)
            return False


async def init():
    status = download_file("https://api.raydium.io/v2/sdk/liquidity/mainnet.json", "liquidity_mainnet.json")
    if status:
        r = await redis.from_url("redis://localhost")
        t = time.time()
        async with r.pipeline(transaction=True) as pipe:
            for key, value in (await get_pool_list()).items():
                pipe.set(f"pool:{key}", pickle.dumps(value))
            await pipe.execute()
        print(f"写入redis数据库完成 耗时{time.time() - t}")


if __name__ == '__main__':
    asyncio.run(init())
