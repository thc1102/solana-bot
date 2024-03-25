import asyncio

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from orm.crud import tasks
from orm.models.tasks import TasksLog
from settings.config import AppConfig
from utils.public import update_snipe_list
from web.utils import update_object, custom_datetime_serializer

router = APIRouter(prefix="/api")

lock = asyncio.Lock()


class ConfigData(BaseModel):
    USE_SNIPE_LIST: bool
    MAX_BUY_RETRIES: int
    MAX_SELL_RETRIES: int
    MICROLAMPORTS: int
    AUTO_TRADING: bool
    AUTO_QUOTE_AMOUNT: float
    AUTO_SELL_STATUS: bool
    CHECK_IF_MINT_IS_RENOUNCED: bool
    POOL_SIZE: int
    AUTO_SELL_TIME: int
    RUN_LP_TIME: int


class TasksData(BaseModel):
    baseMint: str
    amount: float


class DeleteData(BaseModel):
    id: int = None
    ids: int = None


@router.get("/get_config")
async def get_config():
    result = {
        "USE_SNIPE_LIST": AppConfig.USE_SNIPE_LIST,
        "MAX_BUY_RETRIES": AppConfig.MAX_BUY_RETRIES,
        "MAX_SELL_RETRIES": AppConfig.MAX_SELL_RETRIES,
        "MICROLAMPORTS": AppConfig.MICROLAMPORTS,
        "AUTO_TRADING": AppConfig.AUTO_TRADING,
        "AUTO_QUOTE_AMOUNT": AppConfig.AUTO_QUOTE_AMOUNT,
        "AUTO_SELL_STATUS": AppConfig.AUTO_SELL_STATUS,
        "CHECK_IF_MINT_IS_RENOUNCED": AppConfig.CHECK_IF_MINT_IS_RENOUNCED,
        "POOL_SIZE": AppConfig.POOL_SIZE,
        "AUTO_SELL_TIME": AppConfig.AUTO_SELL_TIME,
        "RUN_LP_TIME": AppConfig.RUN_LP_TIME
    }
    return result


@router.post("/set_config")
async def set_config(config: ConfigData):
    async with lock:
        update_object(AppConfig, config)
        logger.info("运行中配置信息已更新")
    return "ok"


@router.get("/get_tasks")
async def get_tasks():
    tasks_list = await tasks.get_tasks()
    # 序列化日期时间字段
    for task in tasks_list:
        task.updatedAt = custom_datetime_serializer(task.updatedAt)
    return tasks_list


@router.post("/create_tasks")
async def create_tasks(tasks_data: TasksData):
    await tasks.create_tasks(tasks_data.dict())
    asyncio.create_task(update_snipe_list())
    return "ok"


@router.post("/delete_tasks")
async def delete_tasks(data: DeleteData):
    await tasks.delete_tasks(data.id)
    asyncio.create_task(update_snipe_list())
    return "ok"


@router.get("/get_tasks_log")
async def get_tasks_log():
    tasks_log_list = await tasks.get_tasks_log()
    # 序列化日期时间字段
    for task_log in tasks_log_list:
        task_log.updatedAt = custom_datetime_serializer(task_log.updatedAt)
    return tasks_log_list


@router.get("/delete_tasks")
async def delete_tasks():
    await tasks.delete_task_log()
    return "ok"
