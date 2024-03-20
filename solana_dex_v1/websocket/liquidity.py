import asyncio
import time

import websockets
from loguru import logger
from solana.rpc.commitment import Finalized, Confirmed
from solana.rpc.types import MemcmpOpts, DataSliceOpts
from solana.rpc.websocket_api import connect
from asyncstdlib import enumerate
from settings.config import Config
from solana_dex_v1.common.constants import RAYDIUM_LIQUIDITY_POOL_V4, SOL_MINT_ADDRESS
from solana_dex_v1.layout.raydium_layout import LIQUIDITY_STATE_LAYOUT_V4

exclude_address_set = set()

async def parse_liqudity_data(data):
    run_timestamp = time.time()
    try:
        pool_state = LIQUIDITY_STATE_LAYOUT_V4.parse(data.result.value.account.data)
        if pool_state.base_mint in exclude_address_set:
            return
        # print(data.result.value.pubkey, pool_state)
        pool_open_time = pool_state.pool_open_time
        if run_timestamp - pool_open_time < 0:
            logger.info(f"查找到流动池 {pool_state} 未开盘 开盘时间 {pool_open_time}")

        if run_timestamp - pool_open_time < 60:
            exclude_address_set.add(pool_state.base_mint)
            # await check_raydium_liquidity(pool_state.baseMint)
            logger.info(f"检测到流动池变动 {pool_state.base_mint} 运行时间 {run_timestamp - pool_open_time} s")
    except Exception as e:
        logger.info(e)

async def run():
    logger.info("监听 Raydium 变化")
    while True:
        try:
            async with connect(Config.RPC_WEBSOCKET_ENDPOINT, max_queue=None) as wss:
                await wss.program_subscribe(
                    RAYDIUM_LIQUIDITY_POOL_V4, Confirmed, "base64",
                    data_slice=DataSliceOpts(length=752, offset=0),
                    filters=[
                        MemcmpOpts(offset=432, bytes="So11111111111111111111111111111111111111112"),
                        MemcmpOpts(offset=560, bytes="srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"),
                        MemcmpOpts(offset=0, bytes="21D35quxec7")
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
