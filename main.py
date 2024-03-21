import asyncio

from loguru import logger
from tortoise import Tortoise

from orm.crud.raydium_pool import RaydiumPoolHelper
from solana_dex_v1.common.constants import SOL_MINT_ADDRESS
from solana_dex_v1.layout.serum_layout import MARKET_STATE_LAYOUT_V3
from solana_dex_v1.websocket import openbook, liquidity


async def run():
    # await Tortoise.init(
    #     db_url='sqlite://db.sqlite3',
    #     modules={'models': ['orm.models.raydium_pool']}
    # )
    # pool_count = await RaydiumPoolHelper.get_pool_count()
    # logger.info(f"当前缓存流动池条数 {pool_count}")
    stop_event = asyncio.Event()
    asyncio.create_task(openbook.run())
    # asyncio.create_task(liquidity.run())
    await stop_event.wait()


if __name__ == '__main__':
    asyncio.run(run())
