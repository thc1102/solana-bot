import time

from loguru import logger
from solders.pubkey import Pubkey

from orm.tasks import Tasks
from settings.config import AppConfig
from solana_dex.layout.raydium import LIQUIDITY_STATE_LAYOUT_V4
from solana_dex.snipe_processor import SnipeProcessor
from solana_dex.transaction_processor import TransactionProcessor
from utils.public import generate_pool_data


class TasksProcessor:
    # 用于排除已经处理过的地址
    exclude_address_set = set()

    @staticmethod
    async def liqudity_tasks(liqudity_id: str, liqudity_info: LIQUIDITY_STATE_LAYOUT_V4):
        if liqudity_id in TasksProcessor.exclude_address_set:
            return
        if liqudity_info.get("status") == 6:
            TasksProcessor.exclude_address_set.add(liqudity_id)
        base_mint = str(Pubkey.from_bytes(liqudity_info.baseMint))
        pool_open_time = liqudity_info.poolOpenTime
        pool_open_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pool_open_time))
        now_timestamp = time.time()
        # 根据流动性信息进行后续处理
        pool_info = await generate_pool_data(base_mint, liqudity_id, liqudity_info)
        matching_time = time.time() - now_timestamp
        open_status = now_timestamp - pool_open_time >= 0
        if pool_info:
            if AppConfig.LOG_FILTER:
                logger.info(f"代币 {base_mint} 流动性变化 开放时间 {pool_open_time_str} 匹配成功 耗时 {matching_time:.3f}")
            if open_status and AppConfig.USE_SNIPE_LIST:
                task_info = SnipeProcessor.no_matched_snipe_map.get(base_mint, None)
                if task_info:
                    logger.info(f"模式B 狙击任务 {base_mint}")
                    status = await TransactionProcessor.append_buy(pool_info, task_info)
                    if status:
                        await Tasks.filter(baseMint=base_mint).update(status=1)
        else:
            # 如果匹配失败会在下一次流动性变化时再次匹配
            if AppConfig.LOG_FILTER:
                logger.error(f"代币 {base_mint} 流动性变化 开放时间 {pool_open_time_str} 匹配失败")
            TasksProcessor.exclude_address_set.discard(liqudity_id)
