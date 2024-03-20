import asyncio
import time

import websockets
from asyncstdlib import enumerate
from construct import Bytes
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Finalized
from solana.rpc.websocket_api import connect
from solders.pubkey import Pubkey

from raydium.layout import LIQUIDITY_STATE_LAYOUT_V4

from loguru import logger

DEFAULT_PUBLIC_LIST = [Pubkey.from_string("11111111111111111111111111111111"),
                       Pubkey.from_string("So11111111111111111111111111111111111111112")]

START_TIME = 50


async def parse_raydium_data(data: Bytes):
    run_timestamp = time.time()
    try:
        pool_state = LIQUIDITY_STATE_LAYOUT_V4.parse(data)
        pool_open_time = pool_state.poolOpenTime
        print(pool_state)

        # 跳过默认地址
        if pool_state.baseMint in DEFAULT_PUBLIC_LIST:
            return
        if run_timestamp - pool_open_time < 0:
            logger.info(f"查找到流动池 {pool_state} 未开盘 开盘时间 {pool_open_time}")
            print(pool_state)

        if run_timestamp - pool_open_time < START_TIME:
            # await check_raydium_liquidity(pool_state.baseMint)
            logger.info(f"检测到流动池变动 {pool_state.baseMint} 运行时间 {run_timestamp-pool_open_time} s")
    except Exception as e:
        # 遇见无法解析的直接跳过 不处理
        pass


async def check_raydium_liquidity(pubkey):
    async with AsyncClient("wss://mainnet.helius-rpc.com/?api-key=662f50ce-8a1d-4d1d-8d28-ec62db019c7e") as client:
        try:
            res = await client.get_account_info(pubkey)
            print(res)
        except Exception as e:
            print(f"An error occurred: {e}")

async def main():
    while True:
        try:
            async with connect(
                    "wss://mainnet.helius-rpc.com/?api-key=662f50ce-8a1d-4d1d-8d28-ec62db019c7e") as websocket:
                await websocket.program_subscribe(
                    Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"),
                    Finalized, "base64"
                )
                first_resp = await websocket.recv()
                subscription_id = first_resp[0].result
                async for idx, updated_account_info in enumerate(websocket):
                    try:
                        data = updated_account_info[0].result.value.account.data
                        asyncio.create_task(parse_raydium_data(data))
                        # await parse_raydium_data(data)
                    except Exception:
                        pass
                await websocket.program_unsubscribe(subscription_id)
        except (ConnectionResetError, websockets.exceptions.ConnectionClosedError) as e:
            logger.error(f"Error occurred: {e}. Retrying...")
            continue
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")


asyncio.run(main())
