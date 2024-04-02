import asyncio
import datetime
from typing import Union, Any

from loguru import logger

from orm.crud import update_task_status
from orm.tasks import Tasks
from settings.config import AppConfig
from settings.global_variables import GlobalVariables

lock = asyncio.Lock()


async def update_snipe_list():
    # 刷新狙击列表
    new_snipe_list = {}
    all_task = await Tasks.filter(status=0).all()
    for task in all_task:
        new_snipe_list[task.baseMint] = task
    async with lock:
        GlobalVariables.snipe_list = new_snipe_list
    logger.info(f"狙击列表更新 当前待狙击数量 {len(all_task)} 狙击状态 {AppConfig.USE_SNIPE_LIST}")


async def update_snipe_status(task_info: Tasks):
    # 狙击完成更新状态使用
    async with lock:
        GlobalVariables.snipe_list.pop(task_info.baseMint, None)
    await update_task_status(task_info.id, 1)


def update_object(obj, data):
    # 更新对象属性值
    for field in obj.__fields__:
        if field in data.__fields__:
            setattr(obj, field, getattr(data, field))


def custom_datetime_serializer(dt: Union[datetime, None]) -> Any:
    # 序列化日期时间
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')
