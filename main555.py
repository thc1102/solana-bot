import asyncio

from solders.pubkey import Pubkey

from solana_dex_v1.common.constants import SOL_MINT_ADDRESS
from solana_dex_v1.layout.serum_layout import MARKET_STATE_LAYOUT_V3
from solana_dex_v1.solana.solana_client import SolanaRPCClient
from solana_dex_v1.websocket import openbook, liquidity


async def run():
    stop_event = asyncio.Event()
    print(await SolanaRPCClient.get_account_info(Pubkey.from_string("9hM9HAAE8Dd9ou2j4bwviekSnC3y2Mo8CNtJCuERfR2W")))
    await stop_event.wait()


if __name__ == '__main__':
    asyncio.run(run())
