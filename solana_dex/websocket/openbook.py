import asyncio
import json

import websockets
from asyncstdlib import enumerate
from loguru import logger
from solana.rpc.commitment import Confirmed
from solana.rpc.types import MemcmpOpts, DataSliceOpts
from solana.rpc.websocket_api import connect

from settings.config import AppConfig
from solana_dex.common.constants import SOL_MINT_ADDRESS, OPENBOOK_MARKET
from solana_dex.layout.market import MARKET_STATE_LAYOUT_V3
from solana_dex.model.pool import PoolInfo
from utils.redis_utils import RedisFactory


async def parse_openbook_data(data):
    # 解析订阅的 OpenBook 数据
    try:
        info = MARKET_STATE_LAYOUT_V3.parse(data.result.value.account.data)
        async with RedisFactory() as r:
            pool_info = PoolInfo.from_market(info).to_json()
            await r.setnx(f"pool:{pool_info.get('baseMint')}", json.dumps(pool_info))
    except Exception as e:
        logger.error(e)


async def handle_openbook_data(data):
    # 处理订阅的 OpenBook 数据
    try:
        await parse_openbook_data(data)
    except Exception as e:
        logger.error(f"解析 OpenBook 数据时发生错误: {e}")


async def subscribe_openbook(wss):
    # 订阅 OpenBook 数据
    await wss.program_subscribe(
        OPENBOOK_MARKET, Confirmed, "base64",
        data_slice=DataSliceOpts(length=388, offset=0),
        filters=[MemcmpOpts(offset=85, bytes=str(SOL_MINT_ADDRESS))]
    )
    first_resp = await wss.recv()
    subscription_id = first_resp[0].result
    logger.info(f"订阅成功，subscription_id: {subscription_id}")
    async for idx, updated_info in enumerate(wss):
        asyncio.create_task(handle_openbook_data(updated_info[0]))
    return subscription_id


async def connect_and_subscribe():
    # 连接到 RPC WebSocket 并订阅 OpenBook 数据
    while True:
        try:
            async with connect(AppConfig.RPC_WEBSOCKET_ENDPOINT, max_queue=10 ** 3) as wss:
                logger.info("成功连接到 RPC WebSocket")
                subscription_id = await subscribe_openbook(wss)
                await wss.program_unsubscribe(subscription_id)
        except (ConnectionResetError, websockets.exceptions.ConnectionClosedError) as e:
            logger.error(f"连接或订阅期间发生错误: {e}, 正在重试...")
            await asyncio.sleep(5)  # 等待一段时间后重试
        except Exception as e:
            logger.error(f"连接或订阅期间发生意外错误: {e}")


if __name__ == '__main__':
    asyncio.run(connect_and_subscribe())
