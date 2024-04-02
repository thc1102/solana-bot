import asyncio
import json
import pickle

import websockets
from loguru import logger
from solana.rpc.commitment import Processed, Confirmed
from solana.rpc.types import MemcmpOpts, DataSliceOpts
from solana.rpc.websocket_api import connect
from asyncstdlib import enumerate
from solders.pubkey import Pubkey

from solana_dex.model.pool import PoolInfo
from utils.redis_utils import RedisFactory
# from settings.config import AppConfig
from solana_dex.common.constants import SOL_MINT_ADDRESS, OPENBOOK_MARKET
from solana_dex.layout.market import MARKET_STATE_LAYOUT_V3


async def parse_openbook_data(data):
    try:
        info = MARKET_STATE_LAYOUT_V3.parse(data.result.value.account.data)
        print(PoolInfo.from_market(info).__dict__)
        async with RedisFactory() as r:
            pool_info = PoolInfo.from_market(info).to_json()
            await r.setnx(f"pool:{pool_info.get('baseMint')}", json.dumps(pool_info))
    except Exception as e:
        logger.exception(e)


async def run():
    logger.info("监听 OpenBook 变化")
    while True:
        try:
            async with connect(
                    "wss://aged-few-sailboat.solana-mainnet.quiknode.pro/a59a384a0e707c877100881079c24ebfee00eb1b/") as wss:
                await wss.program_subscribe(
                    OPENBOOK_MARKET, Confirmed, "base64",
                    data_slice=DataSliceOpts(length=388, offset=0),
                    filters=[MemcmpOpts(offset=85, bytes=str(SOL_MINT_ADDRESS))]
                )
                first_resp = await wss.recv()
                subscription_id = first_resp[0].result
                async for idx, updated_info in enumerate(wss):
                    # asyncio.create_task(parse_openbook_data(updated_info[0]))
                    await parse_openbook_data(updated_info[0])
                await wss.program_unsubscribe(subscription_id)
        except (ConnectionResetError, websockets.exceptions.ConnectionClosedError) as e:
            logger.error(f"发生错误 {e} 正在重试...")
            continue
        except Exception as e:
            logger.error(f"发生意外错误 {e}")


asyncio.run(run())
