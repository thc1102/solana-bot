import asyncio
import time

from solders.pubkey import Pubkey

from settings.config import AppConfig
from solana_dex.raydium.models import ApiPoolInfo
from solana_dex.raydium.swap_core import SwapCore
from solana_dex.solana.wallet import Wallet
from settings.global_variables import GlobalVariables

# 测试购买
test_num = False

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
    async def append_buy(api_pool_info: ApiPoolInfo, check_buy_repeat: bool = True):
        try:
            if check_buy_repeat:
                if api_pool_info.baseMint in exclude_buy_set:
                    return
            # 避免重复购买
            exclude_buy_set.add(api_pool_info.baseMint)
            global test_num
            if test_num:
                return
            if AppConfig.USE_SNIPE_LIST:
                pass
            if not AppConfig.AUTO_TRADING:
                return
            wallet = GlobalVariables.default_wallet
            swap = SwapCore(wallet, api_pool_info, AppConfig.MICROLAMPORTS)
            buy = await send_with_retry(lambda: swap.buy(api_pool_info.baseMint, 0.01),
                                        max_attempts=AppConfig.MAX_BUY_RETRIES)
            # 购买完成后去重
            exclude_buy_set.discard(api_pool_info.baseMint)
            if not buy:
                return False
            test_num = True
            # 等待售出
            await asyncio.sleep(AppConfig.AUTO_SELL_TIME)
            # 创建售出任务
            asyncio.create_task(TransactionProcessor.append_sell(api_pool_info))
        except Exception as e:
            print(e)

    @staticmethod
    async def append_sell(api_pool_info: ApiPoolInfo, swap: SwapCore = None):
        wallet = GlobalVariables.default_wallet
        if not swap:
            swap = SwapCore(wallet, api_pool_info, AppConfig.MICROLAMPORTS)
        await send_with_retry(lambda: swap.sell(api_pool_info.baseMint),
                              max_attempts=AppConfig.MAX_SELL_RETRIES,
                              delay=0.2)
