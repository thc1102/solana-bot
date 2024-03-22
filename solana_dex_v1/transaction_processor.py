import asyncio

from solders.pubkey import Pubkey

from settings.config import AppConfig
from solana_dex_v1.raydium.models import ApiPoolInfo
from solana_dex_v1.raydium.swap_core import SwapCore
from solana_dex_v1.solana.wallet import Wallet


class TransactionProcessor:
    """
    交易处理器用于处理各种买卖任务
    """

    @staticmethod
    async def append_buy(api_pool_info: ApiPoolInfo):
        wallet = Wallet(AppConfig.PRIVATE_KEY)
        asyncio.create_task(SwapCore.buy(Pubkey.from_string("So11111111111111111111111111111111111111112"),
                                         api_pool_info.baseMint,
                                         10.0,
                                         wallet.get_keypair(),
                                         api_pool_info))

    @staticmethod
    async def append_sell():
        asyncio.create_task(SwapCore.sell())
