import asyncio

from solders.pubkey import Pubkey
from spl.token._layouts import MINT_LAYOUT

from solana_dex.solana.solana_client import SolanaRPCClient


async def test1():
    resp = await SolanaRPCClient.get_account_info(Pubkey.from_string("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"))
    MINT_LAYOUT.parse(resp.value.data)
    print(resp)


if __name__ == '__main__':
    asyncio.run(test1())
