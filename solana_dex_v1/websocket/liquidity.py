import asyncio
import pickle
import time

import websockets
from loguru import logger
from solana.rpc.commitment import Processed
from solana.rpc.types import MemcmpOpts, DataSliceOpts
from solana.rpc.websocket_api import connect
from asyncstdlib import enumerate
from solders.pubkey import Pubkey

from db.redis_utils import RedisFactory
from solana_dex_v1.common.constants import RAYDIUM_LIQUIDITY_POOL_V4
from solana_dex_v1.layout.raydium import LIQUIDITY_STATE_LAYOUT_V4
from solana_dex_v1.model.pool import PoolInfo

# 定义一个set用于排除已监听到的池
exclude_address_set = set()


async def update_db_pool_data(base_mint, pool_info):
    async with RedisFactory() as r:
        await r.setnx(f"pool:{base_mint}", pickle.dumps(pool_info))


async def generate_pool_data(base_mint, liqudity_id, liqudity_info):
    # 生成池数据
    async with RedisFactory() as r:
        pool_info = await r.get(f"pool:{base_mint}")
        if pool_info:
            return pickle.loads(pool_info)
        market_data = await r.get(f"market:{base_mint}")
        if market_data:
            market_info = pickle.loads(market_data)
            pool_info = PoolInfo.from_liquidity_and_market(liqudity_id, market_info, liqudity_info)
            asyncio.create_task(update_db_pool_data(base_mint, pool_info))
            return pool_info
    return None


async def parse_liqudity_data(data):
    now_timestamp = time.time()
    try:
        liqudity_id = str(data.result.value.pubkey)
        base_mint = str(Pubkey.from_bytes(liqudity_info.baseMint))
        if liqudity_id in exclude_address_set:
            return
        exclude_address_set.add(liqudity_id)
        liqudity_info = LIQUIDITY_STATE_LAYOUT_V4.parse(data.result.value.account.data)
        pool_open_time = liqudity_info.poolOpenTime
        pool_open_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pool_open_time))
        pool_info = await generate_pool_data(base_mint, liqudity_id, liqudity_info)
        matching_time = time.time() - now_timestamp
        if pool_info:
            logger.info(
                f"监听到 {base_mint} 流动性变化 匹配成功 开放时间 {pool_open_time_str} 耗时 {matching_time:.3f}")
            return
        logger.warning(
            f"监听到 {base_mint} 流动性变化 匹配失败 开放时间 {pool_open_time_str} 耗时 {matching_time:.3f}")
        exclude_address_set.discard(liqudity_id)
    except Exception as e:
        logger.error(e)


async def run():
    logger.info("监听 Raydium 变化")
    while True:
        try:
            async with connect(
                    "wss://dimensional-frequent-wave.solana-mainnet.quiknode.pro/ab01b5056e35be398d8fa71f3d305c7848bf23fb/") as wss:
                await wss.program_subscribe(
                    RAYDIUM_LIQUIDITY_POOL_V4, Processed, "base64",
                    data_slice=DataSliceOpts(length=752, offset=0),
                    filters=[
                        MemcmpOpts(offset=432, bytes="So11111111111111111111111111111111111111112"),
                        MemcmpOpts(offset=560, bytes="srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"),
                    ]
                )
                first_resp = await wss.recv()
                subscription_id = first_resp[0].result
                async for idx, updated_info in enumerate(wss):
                    asyncio.create_task(parse_liqudity_data(updated_info[0]))
                await wss.program_unsubscribe(subscription_id)
        except (ConnectionResetError, websockets.exceptions.ConnectionClosedError) as e:
            logger.error(f"发生错误 {e} 正在重试...")
            continue
        except Exception as e:
            logger.error(f"发生意外错误 {e}")


asyncio.run(run())
