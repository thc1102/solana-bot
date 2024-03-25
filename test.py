import asyncio

from solders.pubkey import Pubkey

from solana_dex.layout.solana_layout import MINT_LAYOUT
from solana_dex.solana.solana_client import SolanaRPCClient


async def test1():
    resp = await SolanaRPCClient.get_account_info(Pubkey.from_string("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"))
    mint_info = MINT_LAYOUT.parse(resp.value.data)
    if mint_info.mintAuthorityOption == 0:
        return True
    else:
        return False




if __name__ == '__main__':
    asyncio.run(test1())
