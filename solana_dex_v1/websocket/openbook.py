import asyncio

import websockets
from loguru import logger
from solana.rpc.commitment import Finalized, Processed
from solana.rpc.types import MemcmpOpts, DataSliceOpts
from solana.rpc.websocket_api import connect
from asyncstdlib import enumerate

from orm.crud.raydium_pool import RaydiumPoolHelper
from settings.config import Config
from solana_dex_v1.common.constants import OPENBOOK_MARKET, SOL_MINT_ADDRESS
from solana_dex_v1.layout.serum_layout import MARKET_STATE_LAYOUT_V3

exclude_address_set = set()


async def parse_openbook_data(data):
    try:
        info = MARKET_STATE_LAYOUT_V3.parse(data.result.value.account.data)
        if info.base_mint in exclude_address_set:
            return
        if not await RaydiumPoolHelper.get_pool_by_mint(str(info.base_mint)):
            return
        print(data.result.value.pubkey, info.base_mint)
        exclude_address_set.add(info.base_mint)
    except Exception as e:
        logger.exception(e)


async def run():
    logger.info("监听 OpenBook 变化")
    while True:
        try:
            async with connect(Config.RPC_WEBSOCKET_ENDPOINT, max_queue=None) as wss:
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
