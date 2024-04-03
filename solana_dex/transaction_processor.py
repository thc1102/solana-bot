import asyncio
import pickle

from loguru import logger

from orm.crud import update_task_status, create_task_log
from orm.tasks import Tasks
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.model.pool import PoolInfo
from solana_dex.swap.swap_core import SwapCore
from utils.client_utils import AsyncClientFactory
from utils.public import update_snipe_status


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
    async def append_buy(pool_info: PoolInfo, task_info: Tasks, check_buy_repeat: bool = True):
        try:
            if check_buy_repeat:
                if pool_info.baseMint in TransactionProcessor.exclude_buy_set:
                    return False
            # 避免重复购买
            TransactionProcessor.exclude_buy_set.add(pool_info.baseMint)
            # 获取默认钱包地址
            wallet = GlobalVariables.default_wallet
            async with AsyncClientFactory() as client:
                swap = SwapCore(client, wallet, pool_info, jito_status=AppConfig.JITO_STATUS,
                                compute_unit_price=AppConfig.MICROLAMPORTS)
                amount = float(task_info.amount)
                # 购买操作
                txn_signature = await send_with_retry(lambda: swap.buy(pool_info.baseMint, amount),
                                                      max_attempts=AppConfig.MAX_BUY_RETRIES)
                # 狙击结束 必须更新状态 不管成功或者失败
                asyncio.create_task(update_snipe_status(task_info))
                # 购买结束后去重
                TransactionProcessor.exclude_buy_set.discard(pool_info.baseMint)
                if not txn_signature:
                    return False
                status = await swap.confirm_transaction(txn_signature)
                # 上链失败等于购买失败
                if status:
                    logger.info(f"{txn_signature} 上链完成")
                    await create_task_log(wallet.pubkey, pool_info.baseMint, str(task_info.amount), "上链完成", 1, 3,
                                          txn_signature)
                else:
                    logger.error(f"{txn_signature} 上链失败")
                    await create_task_log(wallet.pubkey, pool_info.baseMint, str(task_info.amount), "上链失败", 0, 3,
                                          txn_signature)
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
        async with AsyncClientFactory() as client:
            swap = SwapCore(client, wallet, pool_info, jito_status=AppConfig.JITO_STATUS,
                            compute_unit_price=AppConfig.MICROLAMPORTS)
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
                logger.info(f"{txn_signature} 上链完成")
                await create_task_log(wallet.pubkey, pool_info.baseMint, "", "上链完成", 1, 3,
                                      txn_signature)
            else:
                logger.error(f"{txn_signature} 上链失败")
                await create_task_log(wallet.pubkey, pool_info.baseMint, "", "上链完成", 0, 3,
                                      txn_signature)
                return False
        return True
