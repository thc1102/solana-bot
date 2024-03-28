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
from settings.config import AppConfig
from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4, LAMPORTS_PER_SOL
from solana_dex.layout.raydium import LIQUIDITY_STATE_LAYOUT_V4
from solana_dex.layout.solana import MINT_LAYOUT
from solana_dex.model.pool import PoolInfo
from solana_dex.utils.client_utils import AsyncClientFactory

# 定义一个set用于排除已监听到的池
exclude_address_set = set()


async def update_db_pool_data(base_mint, pool_info):
    # 更新redis中池数据
    async with RedisFactory() as r:
        await r.set(f"pool:{base_mint}", pickle.dumps(pool_info))


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


async def check_raydium_liquidity(quote_vault: Pubkey):
    try:
        async with AsyncClientFactory() as client:
            qvalue = await client.get_balance(quote_vault)
            sol = qvalue.value / LAMPORTS_PER_SOL
            if sol > AppConfig.POOL_SIZE:
                return True
        return False
    except:
        return False


async def check_mint_status(mint: Pubkey):
    try:
        async with AsyncClientFactory() as client:
            resp = await client.get_account_info(mint)
            mint_info = MINT_LAYOUT.parse(resp.value.data)
            if mint_info.mintAuthorityOption == 0 and mint_info.freezeAuthorityOption == 0:
                return True
            else:
                return False
    except:
        return False


async def parse_liqudity_data(data):
    now_timestamp = time.time()
    try:
        liqudity_id = str(data.result.value.pubkey)
        if liqudity_id in exclude_address_set:
            return
        exclude_address_set.add(liqudity_id)
        liqudity_info = LIQUIDITY_STATE_LAYOUT_V4.parse(data.result.value.account.data)
        base_mint = str(Pubkey.from_bytes(liqudity_info.baseMint))
        pool_open_time = liqudity_info.poolOpenTime
        pool_open_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pool_open_time))
        pool_info = await generate_pool_data(base_mint, liqudity_id, liqudity_info)
        matching_time = time.time() - now_timestamp
        if pool_info:
            task_list = []
            logger.info(
                f"监听到 {base_mint} 流动性变化 匹配成功 开放时间 {pool_open_time_str} 耗时 {matching_time:.3f}")
            if AppConfig.AUTO_TRADING:
                if now_timestamp - pool_open_time < AppConfig.RUN_LP_TIME:
                    if now_timestamp - pool_open_time < 0:
                        exclude_address_set.discard(liqudity_id)
                    # 流动池检测
                    if AppConfig.POOL_SIZE != 0:
                        task_list.append(check_raydium_liquidity(Pubkey.from_string(pool_info.quoteVault)))
                    # Mint权限检测
                    if AppConfig.CHECK_IF_MINT_IS_RENOUNCED:
                        task_list.append(check_mint_status(Pubkey.from_string(pool_info.baseMint)))
                    if len(task_list) != 0:
                        results = await asyncio.gather(*task_list)
                        if any(result is False for result in results):
                            logger.info(f"{base_mint} 验证未通过")
                            return False
                    logger.info(f"模拟购买{base_mint}")
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
            async with connect(AppConfig.RPC_WEBSOCKET_ENDPOINT) as wss:
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
