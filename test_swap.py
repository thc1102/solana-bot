import asyncio

from loguru import logger
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address

from settings.config import AppConfig
from solana_dex.raydium.swap_core import SwapCore
from solana_dex.solana.wallet import Wallet
from solana_dex.transaction_processor import TransactionProcessor


class ApiPoolInfo:
    def __init__(self):
        self.id = Pubkey.from_string("FyKGP8uNEZB9oj2dzD5H2aS1znshikL3fVKeQpD5Xaqb")
        self.baseMint = Pubkey.from_string("AtVFdJFic9xAK5qvQnNaY3RTz68iEgB5H7mqf7YzKtgg")
        self.quoteMint = Pubkey.from_string("So11111111111111111111111111111111111111112")
        self.lpMint = Pubkey.from_string("5xL7QM4Lyqtf698wZhcG459KDnLKRiGUKyUndyWFSxLZ")
        self.baseDecimals = 4
        self.quoteDecimals = 9
        self.lpDecimals = 6
        self.version = 4
        self.programId = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
        self.authority = Pubkey.from_string("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1")
        self.openOrders = Pubkey.from_string("GUVUkdgn7whVJtEaaBKnQ6RSo6SKTZ3i8c1EesfHb1DB")
        self.targetOrders = Pubkey.from_string("5qK8FSHTtwCVBGauiCpifoQoitioYZVkJPtvCBTRueez")
        self.baseVault = Pubkey.from_string("4MsBW8AURJxVEkxR66QUm5HSL2Mez5GynKdZnas4Dc8T")
        self.quoteVault = Pubkey.from_string("9UHfj3TB7fgAmm7GaTnVVSez8Juw1Qs9fDqHboMFRR4v")
        self.withdrawQueue = Pubkey.from_string("11111111111111111111111111111111")
        self.lpVault = Pubkey.from_string("11111111111111111111111111111111")
        self.marketVersion = 4
        self.marketProgramId = Pubkey.from_string("srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX")
        self.marketId = Pubkey.from_string("DDgV1iQjRsbcCADjf3zHWSLPvpYzRSuWLaUu5kDKgtdf")
        self.marketAuthority = Pubkey.from_string("25knx5odLbzhbRYGc8UtNT9bUVtk4AfM3GpPJar1B3GT")
        self.marketBaseVault = Pubkey.from_string("ELttBrt4N8vdQAJGzRA377WwhBuYGNev1Sn57vWSkmjR")
        self.marketQuoteVault = Pubkey.from_string("GESoEKgtuU65hfBFQxVTx46Qwk76YMBXWtSczXrxbM3Y")
        self.marketBids = Pubkey.from_string("DmHBTaTQZ8XNnWtCpDdbSFJipXtRXrjTz8RvvSMrNguU")
        self.marketAsks = Pubkey.from_string("6etnG79EuQ1s1wueajuBazRxD721REMmmQHFdP1pZDXx")
        self.marketEventQueue = Pubkey.from_string("5bpsLYA6iiYpmsYswFmQFED3vM5jPez2H7UVdh4gexRh")
        self.lookupTableAccount = Pubkey.default()


async def run():
    pool_info = ApiPoolInfo()
    wallet = Wallet(AppConfig.PRIVATE_KEY)
    await wallet.update_token_accounts()
    swap = SwapCore(wallet, pool_info)
    print(wallet.pubkey)

    # puy = await swap.buy(Pubkey.from_string("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"), 0.01)
    # await asyncio.sleep(60)
    # if puy:
    await swap.sell(Pubkey.from_string("AtVFdJFic9xAK5qvQnNaY3RTz68iEgB5H7mqf7YzKtgg"))


if __name__ == '__main__':
    asyncio.run(run())
