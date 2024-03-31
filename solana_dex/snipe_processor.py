import asyncio
import pickle
import time

from loguru import logger

from orm.tasks import Tasks, TasksLog
from solana_dex.model.pool import PoolInfo
from solana_dex.transaction_processor import TransactionProcessor
from utils.redis_utils import RedisFactory


class SnipeProcessor:
    # 未匹配到流动池则使用此列表
    no_matched_snipe_map = {}
    look = asyncio.Lock()
    _snipe_map = {}
    _run_status = False
    _refresh_task = None

    async def start(self):
        if not SnipeProcessor._run_status:
            SnipeProcessor._run_status = True
            SnipeProcessor._refresh_task = asyncio.create_task(self._refresh_snipe_map())
            logger.info("狙击模式已开启")

    async def stop(self):
        SnipeProcessor._run_status = False
        snipe_map_copy = dict(SnipeProcessor._snipe_map)
        for mint, task in snipe_map_copy.items():
            task.cancel()
        SnipeProcessor._refresh_task.cancel()
        await asyncio.sleep(0.05)
        SnipeProcessor._snipe_map = {}
        SnipeProcessor.no_matched_snipe_map = {}

    async def update_snipe_map(self):
        try:
            task_list = await Tasks.all()
            # 获取狙击列表
            for task in task_list:
                # 判断是否已经创建任务
                if task.baseMint not in SnipeProcessor._snipe_map:
                    async with RedisFactory() as r:
                        pool_info = await r.get(f"pool:{task.baseMint}")
                        if not pool_info:
                            continue
                        pool_info = pickle.loads(pool_info)
                        if not pool_info.poolOpenTime:
                            continue
                        start_sleep = pool_info.poolOpenTime - time.time()
                        if start_sleep < 0:
                            await Tasks.filter(baseMint=task.baseMint).update(status=3)
                            await asyncio.to_thread(self._delete_snipe_task, task.baseMint)
                        elif 5 < start_sleep < 30:
                            task_obj = self._create_snipe_task(pool_info, task, start_sleep)
                            snipe_task = asyncio.create_task(task_obj)
                            SnipeProcessor._snipe_map[task.baseMint] = snipe_task
                            await Tasks.filter(baseMint=task.baseMint).update(status=2)
            new_snipe_list = {}
            for task in await Tasks.filter(status=0).all():
                new_snipe_list[task.baseMint] = task
            async with SnipeProcessor.look:
                SnipeProcessor.no_matched_snipe_map = new_snipe_list
        except Exception as e:
            logger.error(e)

    async def _refresh_snipe_map(self):
        try:
            while SnipeProcessor._run_status:
                await self.update_snipe_map()
                await asyncio.sleep(2)
            else:
                logger.info("狙击模式已停止")
        except asyncio.CancelledError:
            logger.info("狙击模式已关闭")

    def _delete_snipe_task(self, mint):
        if mint in SnipeProcessor._snipe_map:
            del SnipeProcessor._snipe_map[mint]

    async def _create_snipe_task(self, pool_info: PoolInfo, task_info: Tasks, sleep: int):
        try:
            sleep = sleep + 0.5
            logger.info(f"模式A 狙击任务 {task_info.baseMint} 已开启 等待时间 {sleep}")
            await TransactionProcessor.append_buy(pool_info, task_info, sleep=sleep)
        except asyncio.CancelledError:
            logger.info(f"狙击任务 {task_info.baseMint} 已关闭")

    async def sync_db_to_task(self):
        try:
            task_list = await Tasks.all()
            task_mints = {item.baseMint for item in task_list}
            snipe_map_copy = dict(SnipeProcessor._snipe_map)
            for mint, snipe_task in snipe_map_copy.items():
                if mint not in task_mints:
                    snipe_task.cancel()
                    await asyncio.to_thread(self._delete_snipe_task, mint)
            new_snipe_list = {}
            for task in await Tasks.filter(status=0).all():
                new_snipe_list[task.baseMint] = task
            async with SnipeProcessor.look:
                SnipeProcessor.no_matched_snipe_map = new_snipe_list
        except Exception as e:
            logger.error(e)
