import asyncio

from solana_dex_v1.common.constants import SOL_MINT_ADDRESS
from solana_dex_v1.layout.serum_layout import MARKET_STATE_LAYOUT_V3
from solana_dex_v1.websocket import openbook, liquidity


async def run():
    stop_event = asyncio.Event()
    # asyncio.create_task(openbook.run())
    asyncio.create_task(liquidity.run())
    await stop_event.wait()


if __name__ == '__main__':
    asyncio.run(run())
