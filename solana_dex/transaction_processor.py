import asyncio
import pickle

from loguru import logger

from orm.tasks import Tasks
from utils.redis_utils import RedisFactory
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.model.pool import PoolInfo
from solana_dex.raydium.swap_core import SwapCore
from solana_dex.utils.client_utils import AsyncClientFactory


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

    exclude_buy_set = set()

    @staticmethod
    async def append_buy(pool_info: PoolInfo, task_info: Tasks, check_buy_repeat: bool = True, sleep=0):
        try:
            if check_buy_repeat:
                if pool_info.baseMint in TransactionProcessor.exclude_buy_set:
                    return False
            # 避免重复购买
            TransactionProcessor.exclude_buy_set.add(pool_info.baseMint)
            # 获取默认钱包地址
            wallet = GlobalVariables.default_wallet
            async with AsyncClientFactory(blockhash_status=True) as client:
                swap = SwapCore(client, wallet, pool_info, compute_unit_price=AppConfig.MICROLAMPORTS)
                amount = float(task_info.amount)
                if sleep != 0:
                    # 进行延迟等待
                    await asyncio.sleep(sleep)
                #
                txn_signature = await send_with_retry(lambda: swap.buy(pool_info.baseMint, amount),
                                                      max_attempts=AppConfig.MAX_BUY_RETRIES)
                # 购买结束后去重
                TransactionProcessor.exclude_buy_set.discard(pool_info.baseMint)
                if not txn_signature:
                    return False
                status = await swap.confirm_transaction(txn_signature)
                # 上链失败等于购买失败
                if status:
                    logger.info(f"{txn_signature} 上链成功")
                else:
                    logger.error(f"{txn_signature} 上链失败")
                    return False
                if not AppConfig.AUTO_SELL_STATUS:
                    return True
                # 创建售出任务
                asyncio.create_task(TransactionProcessor.append_sell(pool_info, AppConfig.AUTO_SELL_TIME))
                return True
        except Exception as e:
            logger.error(e)
            return False

    @staticmethod
    async def append_sell(pool_info: PoolInfo, sleep=0):
        # 获取默认钱包
        wallet = GlobalVariables.default_wallet
        async with AsyncClientFactory(blockhash_status=True) as client:
            swap = SwapCore(client, wallet, pool_info, compute_unit_price=AppConfig.MICROLAMPORTS)
            if sleep != 0:
                await asyncio.sleep(AppConfig.AUTO_SELL_TIME)
            txn_signature = await send_with_retry(lambda: swap.sell(pool_info.baseMint),
                                                  max_attempts=AppConfig.MAX_SELL_RETRIES,
                                                  delay=0.2)
            if not txn_signature:
                return False
            status = await swap.confirm_transaction(txn_signature)
            # 上链失败等于出售失败
            if status:
                logger.info(f"{txn_signature} 上链成功")
            else:
                logger.error(f"{txn_signature} 上链失败")
                return False
        return True

    @staticmethod
    async def web_buy(base_mint: str, amount: float):
        async with RedisFactory() as r:
            pool_info = await r.get(f"pool:{base_mint}")
        if not pool_info:
            return False, "获取流动池信息失败"
        pool_info = pickle.loads(pool_info)
        wallet = GlobalVariables.default_wallet
        async with AsyncClientFactory(blockhash_status=True) as client:
            swap = SwapCore(client, wallet, pool_info, compute_unit_price=AppConfig.MICROLAMPORTS)
            txn_signature = await swap.buy(pool_info.baseMint, amount)
            if not txn_signature:
                return False, "创建任务失败"
            status = await swap.confirm_transaction(txn_signature)
            # 上链失败等于购买失败
            if status:
                logger.info(f"{txn_signature} 上链成功")
                return True, "创建任务成功 上链成功"
            else:
                logger.error(f"{txn_signature} 上链失败")
                return False, "创建任务成功 上链失败"

    @staticmethod
    async def web_sell(base_mint: str, amount: float):
        async with RedisFactory() as r:
            pool_info = await r.get(f"pool:{base_mint}")
        if not pool_info:
            return False, "获取流动池信息失败"
        wallet = GlobalVariables.default_wallet
        pool_info = pickle.loads(pool_info)
        async with AsyncClientFactory(blockhash_status=True) as client:
            swap = SwapCore(client, wallet, pool_info, compute_unit_price=AppConfig.MICROLAMPORTS)
            token_data = wallet.get_token_accounts(base_mint)
            amount = int(amount * (10 ** token_data.decimals))
            txn_signature = await swap.sell(pool_info.baseMint, amount)
            if not txn_signature:
                return False, "创建任务失败"
            status = await swap.confirm_transaction(txn_signature)
            # 上链失败等于出售失败
            if status:
                logger.info(f"{txn_signature} 上链成功")
                return True, "创建任务成功 上链成功"
            else:
                logger.error(f"{txn_signature} 上链失败")
                return False, "创建任务成功 上链失败"

    @staticmethod
    async def web_clone_account():
        async with AsyncClientFactory(blockhash_status=True) as client:
            swap = SwapCore(client, GlobalVariables.default_wallet)
            txn_signature = await swap.close_no_balance_account()
            if not txn_signature:
                return False, "创建任务失败"
            return False, "创建任务成功"
