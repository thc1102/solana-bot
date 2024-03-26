import asyncio

from loguru import logger

from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.raydium.models import ApiPoolInfo
from solana_dex.raydium.swap_core import SwapCore

exclude_buy_set = set()


async def send_with_retry(func, max_attempts=1, delay=0.2):
    attempt = 0
    while attempt < max_attempts:
        result = await func()
        if result:
            return result
        attempt += 1
        await asyncio.sleep(delay)
    return None


class TransactionProcessor:
    """
    交易处理器用于处理各种买卖任务
    """

    @staticmethod
    async def append_buy(api_pool_info: ApiPoolInfo, task_info=None, check_buy_repeat: bool = True):
        try:

            if check_buy_repeat:
                if api_pool_info.baseMint in exclude_buy_set:
                    return
            # 避免重复购买
            exclude_buy_set.add(api_pool_info.baseMint)
            wallet = GlobalVariables.default_wallet
            swap = SwapCore(wallet, api_pool_info, AppConfig.MICROLAMPORTS)
            if task_info:
                amount = float(task_info.amount)
            else:
                amount = AppConfig.AUTO_QUOTE_AMOUNT
            buy = await send_with_retry(lambda: swap.buy(api_pool_info.baseMint, amount),
                                        max_attempts=AppConfig.MAX_BUY_RETRIES)
            # 购买完成后去重
            exclude_buy_set.discard(api_pool_info.baseMint)
            if not buy:
                return False
            if not AppConfig.AUTO_SELL_STATUS:
                return
            # 等待售出
            await asyncio.sleep(AppConfig.AUTO_SELL_TIME)
            # 创建售出任务
            asyncio.create_task(TransactionProcessor.append_sell(api_pool_info))
        except Exception as e:
            logger.error(e)

    @staticmethod
    async def append_sell(api_pool_info: ApiPoolInfo, swap: SwapCore = None):
        wallet = GlobalVariables.default_wallet
        if not swap:
            swap = SwapCore(wallet, api_pool_info, AppConfig.MICROLAMPORTS)
        await send_with_retry(lambda: swap.sell(api_pool_info.baseMint),
                              max_attempts=AppConfig.MAX_SELL_RETRIES,
                              delay=0.2)
