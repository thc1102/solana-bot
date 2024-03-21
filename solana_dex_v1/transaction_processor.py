import asyncio

from solana_dex_v1.raydium.models import ApiPoolInfo
from solana_dex_v1.raydium.swap_core import SwapCore


class TransactionProcessor:
    """
    交易处理器用于处理各种买卖任务
    """

    @staticmethod
    async def append_buy(api_pool_info: ApiPoolInfo):
        asyncio.create_task(SwapCore().buy())

    @staticmethod
    async def append_sell():
        asyncio.create_task(SwapCore().sell())
