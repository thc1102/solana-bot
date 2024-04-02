import asyncio

import websockets
from asyncstdlib import enumerate
from loguru import logger
from solana.rpc.commitment import Processed
from solana.rpc.types import DataSliceOpts
from solana.rpc.websocket_api import connect
# from solana_dex.tasks_processor import TasksProcessor

from solana.common import RAYDIUM_LIQUIDITY_POOL_V4


async def parse_liqudity_data(data):
    try:
        # print(len(data.result.value.account.data),data.result.value)
        # if len(data.result.value.account.data) != 752 and len(data.result.value.account.data) != 2208:
        print(len(data.result.value.account.data), data.result.value)
        # liqudity_info = LIQUIDITY_STATE_LAYOUT_V4.parse(data.result.value.account.data)
        # print(liqudity_info)
        # await TasksProcessor.liqudity_tasks(str(data.result.value.pubkey), liqudity_info)
    except Exception as e:
        logger.error(data)
        logger.error(e)


async def run():
    logger.info("监听 Raydium 变化")
    while True:
        try:
            async with connect(
                    "wss://aged-few-sailboat.solana-mainnet.quiknode.pro/a59a384a0e707c877100881079c24ebfee00eb1b/") as wss:
                await wss.program_subscribe(
                    RAYDIUM_LIQUIDITY_POOL_V4, Processed, "base64",
                    data_slice=DataSliceOpts(length=752, offset=0),
                    # filters=[
                    #     MemcmpOpts(offset=432, bytes="So11111111111111111111111111111111111111112"),
                    #     MemcmpOpts(offset=560, bytes="srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"),
                    # ]
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
