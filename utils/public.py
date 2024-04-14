import asyncio
import datetime
from typing import Union, Any

import httpx
import pytz
from loguru import logger

from orm.crud import update_task_status
from orm.tasks import Tasks
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from utils.client_utils import AsyncClientFactory

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
    # 设置时区为北京时间
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 序列化日期时间
    if dt is None:
        return None
    dt = dt.astimezone(beijing_tz)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


async def is_connected(session, health_uri):
    try:
        response = await session.get(health_uri)
        response.raise_for_status()
    except (httpx.RequestError, httpx.HTTPStatusError) as err:
        pass


async def keep_connection_alive(interval=3):
    async with AsyncClientFactory() as client:
        session = client._provider.session
        endpoint_uri = client._provider.endpoint_uri
        if endpoint_uri.endswith("/"):
            health_uri = endpoint_uri + "health"
        else:
            health_uri = endpoint_uri + "/health"
        while True:
            asyncio.create_task(is_connected(session, health_uri))
            await asyncio.sleep(interval)
