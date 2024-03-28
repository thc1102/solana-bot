import asyncio
import datetime
from typing import Union, Any

from loguru import logger

from orm.tasks import Tasks
from settings.config import AppConfig

lock = asyncio.Lock()


async def update_snipe_list():
    # 刷新狙击列表
    all_task = await Tasks.all()
    logger.info(f"狙击列表 当前狙击数量 {len(all_task)}  狙击状态 {AppConfig.USE_SNIPE_LIST}")


def update_object(obj, data):
    for field in obj.__fields__:
        if field in data.__fields__:
            setattr(obj, field, getattr(data, field))


def custom_datetime_serializer(dt: Union[datetime, None]) -> Any:
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')
