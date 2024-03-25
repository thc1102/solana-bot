import asyncio

from loguru import logger

from orm.crud import tasks
from settings.global_variables import GlobalVariables

lock = asyncio.Lock()


async def update_snipe_list():
    # 刷新狙击列表
    new_snipe_list = {}
    all_task = await tasks.get_tasks()
    for task in all_task:
        new_snipe_list[task.baseMint] = task
    async with lock:
        GlobalVariables.snipe_list = new_snipe_list
    logger.info(f"狙击列表更新完成 当前狙击数量 {len(new_snipe_list)}")
