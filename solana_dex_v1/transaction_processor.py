import asyncio
import pickle

from loguru import logger

from db.redis_utils import RedisFactory
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex_v1.model.pool import PoolInfo
from solana_dex_v1.raydium.swap_core import SwapCore, AccountCore
from solana_dex_v1.utils.client_utils import AsyncClientFactory

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
    async def append_buy(pool_info: PoolInfo, task_info=None, check_buy_repeat: bool = True):
        try:

            if check_buy_repeat:
                if pool_info.baseMint in exclude_buy_set:
                    return
            # 避免重复购买
            exclude_buy_set.add(pool_info.baseMint)
            wallet = GlobalVariables.default_wallet
            async with AsyncClientFactory(blockhash_status=True) as client:
                swap = SwapCore(client, wallet, pool_info, compute_unit_price=AppConfig.MICROLAMPORTS)
                if task_info:
                    amount = float(task_info.amount)
                else:
                    amount = AppConfig.AUTO_QUOTE_AMOUNT
                buy = await send_with_retry(lambda: swap.buy(pool_info.baseMint, amount),
                                            max_attempts=AppConfig.MAX_BUY_RETRIES)
                # 购买完成后去重
                exclude_buy_set.discard(pool_info.baseMint)
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
    async def append_sell(pool_info: PoolInfo):
        wallet = GlobalVariables.default_wallet
        async with AsyncClientFactory(blockhash_status=True) as client:
            swap = SwapCore(client, wallet, pool_info, compute_unit_price=AppConfig.MICROLAMPORTS)
            await send_with_retry(lambda: swap.sell(pool_info.baseMint),
                                  max_attempts=AppConfig.MAX_SELL_RETRIES,
                                  delay=0.2)

    @staticmethod
    async def web_buy(base_mint: str, amount: float):
        async with RedisFactory() as r:
            pool_info = await r.get(f"pool:{base_mint}")
        if not pool_info:
            return False, "获取流动池信息失败"
        pool_info = pickle.loads(pool_info)
        wallet = GlobalVariables.default_wallet
        async with AsyncClientFactory(blockhash_status=True) as client:
            swap = SwapCore(client, wallet, pool_info, AppConfig.MICROLAMPORTS)
            await swap.buy(pool_info.baseMint, amount)
        return True, "ok"

    @staticmethod
    async def web_sell(base_mint: str, amount: float):
        async with RedisFactory() as r:
            pool_info = await r.get(f"pool:{base_mint}")
        if not pool_info:
            return False, "获取流动池信息失败"
        wallet = GlobalVariables.default_wallet
        pool_info = pickle.loads(pool_info)
        async with AsyncClientFactory(blockhash_status=True) as client:
            swap = SwapCore(client, wallet, pool_info, AppConfig.MICROLAMPORTS)
            token_data = wallet.get_token_accounts(base_mint)
            amount = int(amount * (10 ** token_data.decimals))
            await swap.sell(pool_info.baseMint, amount)
        return True, "ok"

    @staticmethod
    async def web_clone_account():
        async with AsyncClientFactory(blockhash_status=True) as client:
            account = AccountCore(client, GlobalVariables.default_wallet)
            await account.clone_no_balance_account()
