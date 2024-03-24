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
        self.id = Pubkey.from_string("DSUvc5qf5LJHHV5e2tD184ixotSnCnwj7i4jJa4Xsrmt")
        self.baseMint = Pubkey.from_string("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82")
        self.quoteMint = Pubkey.from_string("So11111111111111111111111111111111111111112")
        self.lpMint = Pubkey.from_string("83WevmL2JzaEvDmuJUFMxcFNnHqP4xonfvAzKmsPWjwu")
        self.baseDecimals = 4
        self.quoteDecimals = 9
        self.lpDecimals = 6
        self.version = 4
        self.programId = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
        self.authority = Pubkey.from_string("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1")
        self.openOrders = Pubkey.from_string("38p42yoKFWgxw2LCbB96wAKa2LwAxiBArY3fc3eA9yWv")
        self.targetOrders = Pubkey.from_string("Eb9w8q4soG5JpgdQhZcZMDpFcHqDga5drudA5A43buUW")
        self.baseVault = Pubkey.from_string("FBba2XsQVhkoQDMfbNLVmo7dsvssdT39BMzVc2eFfE21")
        self.quoteVault = Pubkey.from_string("GuXKCb9ibwSeRSdSYqaCL3dcxBZ7jJcj6Y7rDwzmUBu9")
        self.withdrawQueue = Pubkey.from_string("11111111111111111111111111111111")
        self.lpVault = Pubkey.from_string("11111111111111111111111111111111")
        self.marketVersion = 4
        self.marketProgramId = Pubkey.from_string("srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX")
        self.marketId = Pubkey.from_string("58sHobBa2KmyE3EKxCpgxn5KGuzudmGHsgqYgrfciyzd")
        self.marketAuthority = Pubkey.from_string("B7af1ADihMVF1xE2243G2ggBkLRFTFgHT8hHbjWzqj1F")
        self.marketBaseVault = Pubkey.from_string("Cr278bTbmgyvTbnt1jqCTsPdqUaB9WN3hbGMjRFontmM")
        self.marketQuoteVault = Pubkey.from_string("EYXT9U31MHRsRSBJ8zafg9paUwYLmWZfJHbSwrJ8mNVb")
        self.marketBids = Pubkey.from_string("EhboNaGqMiw2rqvh7uN6qEsfxpNoCJQBzPbiiSBNCXmW")
        self.marketAsks = Pubkey.from_string("CnsZUH9AUNFqkEE6oExCevcHkMamPJhPFvND6mLT4ikb")
        self.marketEventQueue = Pubkey.from_string("33L8Zi2bnkUX99NJeFmSEwYF6DaNknPXTB5EdsVBfb6e")
        self.lookupTableAccount = Pubkey.default()


async def run():
    pool_info = ApiPoolInfo()
    wallet = Wallet(AppConfig.PRIVATE_KEY)
    await wallet.update_token_accounts()
    swap = SwapCore(wallet, pool_info)

    # puy = await swap.buy(Pubkey.from_string("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"), 0.01)
    # await asyncio.sleep(30)
    # if puy:
    await swap.sell(Pubkey.from_string("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"))


if __name__ == '__main__':
    asyncio.run(run())
