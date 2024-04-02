import asyncio

import websockets
from asyncstdlib import enumerate
from loguru import logger
from solana.rpc.commitment import Processed
from solana.rpc.types import DataSliceOpts, MemcmpOpts
from solana.rpc.websocket_api import connect

from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4

from settings.config import AppConfig
from solana_dex.layout.raydium import LIQUIDITY_STATE_LAYOUT_V4
from solana_dex.tasks_processor import TasksProcessor


async def parse_liquidity_data(data):
    try:
        liquidity_info = LIQUIDITY_STATE_LAYOUT_V4.parse(data.result.value.account.data)
        await TasksProcessor.liquidity_tasks(liquidity_info)
    except Exception as e:
        logger.error(e)


async def handle_liquidity_data(data):
    # 处理订阅的 Liquidity 数据
    try:
        await parse_liquidity_data(data)
    except Exception as e:
        logger.error(f"解析 OpenBook 数据时发生错误: {e}")


async def subscribe_liquidity(wss):
    # 订阅 Liquidity 数据
    # MemcmpOpts(offset=0, bytes="21D35quxec7") 表示只监听流动性变动的数据
    await wss.program_subscribe(
        RAYDIUM_LIQUIDITY_POOL_V4, Processed, "base64",
        data_slice=DataSliceOpts(length=752, offset=0),
        filters=[
            MemcmpOpts(offset=432, bytes="So11111111111111111111111111111111111111112"),
            MemcmpOpts(offset=560, bytes="srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"),
            MemcmpOpts(offset=0, bytes="21D35quxec7")
        ]
    )
    first_resp = await wss.recv()
    subscription_id = first_resp[0].result
    logger.info(f"订阅成功，subscription_id: {subscription_id}")
    async for idx, updated_info in enumerate(wss):
        asyncio.create_task(handle_liquidity_data(updated_info[0]))
    return subscription_id


async def connect_and_subscribe():
    # 连接到 RPC WebSocket 并订阅 OpenBook 数据
    while True:
        try:
            async with connect(AppConfig.RPC_WEBSOCKET_ENDPOINT, max_queue=10 ** 4) as wss:
                logger.info("成功连接到 RPC WebSocket")
                subscription_id = await subscribe_liquidity(wss)
                await wss.program_unsubscribe(subscription_id)
        except (ConnectionResetError, websockets.exceptions.ConnectionClosedError) as e:
            logger.error(f"连接或订阅期间发生错误: {e}, 正在重试...")
            await asyncio.sleep(5)  # 等待一段时间后重试
        except Exception as e:
            logger.error(f"连接或订阅期间发生意外错误: {e}")


if __name__ == '__main__':
    asyncio.run(connect_and_subscribe())
