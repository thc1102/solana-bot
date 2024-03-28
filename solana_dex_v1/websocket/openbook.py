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
from solana_dex_v1.common.constants import SOL_MINT_ADDRESS, OPENBOOK_MARKET
from solana_dex_v1.layout.market import MARKET_STATE_LAYOUT_V3
from solana_dex_v1.model.pool import MarketState


async def parse_openbook_data(data):
    try:
        info = MARKET_STATE_LAYOUT_V3.parse(data.result.value.account.data)
        async with RedisFactory() as r:
            await r.setnx(f"market:{str(Pubkey.from_bytes(info.baseMint))}", pickle.dumps(MarketState(info)))
    except Exception as e:
        logger.exception(e)


async def run():
    logger.info("监听 OpenBook 变化")
    while True:
        try:
            async with connect(
                    "wss://dimensional-frequent-wave.solana-mainnet.quiknode.pro/ab01b5056e35be398d8fa71f3d305c7848bf23fb/") as wss:
                await wss.program_subscribe(
                    OPENBOOK_MARKET, Processed, "base64",
                    data_slice=DataSliceOpts(length=388, offset=0),
                    filters=[MemcmpOpts(offset=85, bytes=str(SOL_MINT_ADDRESS))]
                )
                first_resp = await wss.recv()
                subscription_id = first_resp[0].result
                async for idx, updated_info in enumerate(wss):
                    asyncio.create_task(parse_openbook_data(updated_info[0]))
                await wss.program_unsubscribe(subscription_id)
        except (ConnectionResetError, websockets.exceptions.ConnectionClosedError) as e:
            logger.error(f"发生错误 {e} 正在重试...")
            continue
        except Exception as e:
            logger.error(f"发生意外错误 {e}")


