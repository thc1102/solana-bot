import asyncio
import json
import time

from aiocache import Cache
from loguru import logger
from solders.pubkey import Pubkey

from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.layout.raydium import LIQUIDITY_STATE_LAYOUT_V4
from solana_dex.model.pool import PoolInfo
from solana_dex.transaction_processor import TransactionProcessor
from utils.redis_utils import RedisFactory


class TasksProcessor:
    # 用于排除已经处理过的地址
    exclude_address_set = set()
    # 自动过期的字典
    expire_cache = Cache(Cache.MEMORY)

    @staticmethod
    async def liquidity_tasks(liquidity_info: LIQUIDITY_STATE_LAYOUT_V4):
        if await TasksProcessor.expire_cache.exists(liquidity_info.baseMint):
            # logger.debug(f"{liquidity_info.baseMint} 60秒内检测到一次 跳过再次检测")
            return
        await TasksProcessor.expire_cache.set(liquidity_info.baseMint, True, ttl=60)
        if not AppConfig.USE_SNIPE_LIST:
            return
        task_info = GlobalVariables.snipe_list.get(str(liquidity_info.baseMint))
        if task_info is None:
            return
        async with RedisFactory() as redis:
            pool_info_bytes = await redis.get(f"pool:{liquidity_info.baseMint}")
        if pool_info_bytes is None:
            logger.error(f"{liquidity_info.baseMint} 未匹配到池key信息")
            return
        logger.info(f"匹配到狙击任务 {liquidity_info.baseMint}")
        pool_info = PoolInfo.from_json(json.loads(pool_info_bytes))
        await TransactionProcessor.append_buy(pool_info, task_info)
