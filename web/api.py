import asyncio

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from orm.tasks import Tasks, TasksLog
from settings.config import AppConfig
from utils.public import update_snipe_list, update_object, custom_datetime_serializer

router = APIRouter(prefix="/api")

lock = asyncio.Lock()


class ConfigData(BaseModel):
    USE_SNIPE_LIST: bool
    MAX_BUY_RETRIES: int
    MAX_SELL_RETRIES: int
    MICROLAMPORTS: int
    AUTO_SELL_STATUS: bool
    AUTO_SELL_TIME: int
    JITO_STATUS: bool
    JITO_BUY_TIP_AMOUNT: float
    JITO_SELL_TIP_AMOUNT: float


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
        "AUTO_SELL_STATUS": AppConfig.AUTO_SELL_STATUS,
        "AUTO_SELL_TIME": AppConfig.AUTO_SELL_TIME,
        "JITO_STATUS": AppConfig.JITO_STATUS,
        "JITO_BUY_TIP_AMOUNT": AppConfig.JITO_BUY_TIP_AMOUNT,
        "JITO_SELL_TIP_AMOUNT": AppConfig.JITO_SELL_TIP_AMOUNT,
    }
    return result


@router.post("/set_config")
async def set_config(config: ConfigData):
    if config.USE_SNIPE_LIST:
        await update_snipe_list()
    async with lock:
        update_object(AppConfig, config)
        logger.info(f"运行中配置信息已更新 当前信息{config.__dict__}")
    return "配置更新完成"


@router.get("/get_tasks")
async def get_tasks():
    tasks_list = await Tasks.all().order_by("-updatedAt")
    # 序列化日期时间字段
    for task in tasks_list:
        task.updatedAt = custom_datetime_serializer(task.updatedAt)
    return tasks_list


@router.post("/create_tasks")
async def create_tasks(tasks_data: TasksData):
    await Tasks.create(**tasks_data.dict())
    asyncio.create_task(update_snipe_list())
    return "狙击任务创建完成"


@router.post("/delete_tasks")
async def delete_tasks(data: DeleteData):
    await Tasks.filter(id=data.id).delete()
    asyncio.create_task(update_snipe_list())
    return "狙击任务已删除"


@router.get("/get_tasks_log")
async def get_tasks_log():
    tasks_log_list = await TasksLog.all().order_by("-updatedAt")
    # 序列化日期时间字段
    for task_log in tasks_log_list:
        task_log.updatedAt = custom_datetime_serializer(task_log.updatedAt)
    return tasks_log_list


@router.get("/delete_tasks_log")
async def delete_tasks_log():
    await TasksLog.all().delete()
    return "日志记录已全部清空"
