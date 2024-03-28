import asyncio

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from orm.tasks import Tasks, TasksLog
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.snipe_processor import SnipeProcessor
from solana_dex.transaction_processor import TransactionProcessor
from utils.public import update_snipe_list, update_object, custom_datetime_serializer

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


class payDate(BaseModel):
    mint: str
    amount: float


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
    if config.USE_SNIPE_LIST:
        await SnipeProcessor().start()
    else:
        await SnipeProcessor().stop()
    async with lock:
        update_object(AppConfig, config)
        logger.info("运行中配置信息已更新")
    return "ok"


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
    return "ok"


@router.post("/delete_tasks")
async def delete_tasks(data: DeleteData):
    await SnipeProcessor().sync_db_to_task()
    await Tasks.filter(id=data.id).delete()
    asyncio.create_task(update_snipe_list())
    return "ok"


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
    return "ok"


@router.get("/get_wallet")
async def get_wallet():
    wallet = {
        "pubkey": str(GlobalVariables.default_wallet.pubkey),
        "sol": await GlobalVariables.default_wallet.get_sol_balance()
    }
    return wallet


@router.get("/get_token")
async def get_token():
    await GlobalVariables.default_wallet.update_token_accounts()
    account_list = []
    for _, data in GlobalVariables.default_wallet.token_data.items():
        account_list.append(
            {
                "label": data.mint,
                "value": {"mint": data.mint, "amount": data.uiAmount}
            }
        )
    return account_list


@router.post("/buy")
async def buy(data: payDate):
    if data.amount <= 0:
        return "输入的数量不合法"
    status, msg = await TransactionProcessor.web_buy(data.mint, data.amount)
    if status:
        return "购买任务已下发"
    else:
        return msg


@router.post("/sell")
async def sell(data: payDate):
    if data.amount <= 0:
        return "输入的数量不合法"
    status, msg = await TransactionProcessor.web_sell(data.mint, data.amount)
    if status:
        return "出售任务已下发"
    else:
        return msg


@router.get("/clone_account")
async def clone_account():
    asyncio.create_task(TransactionProcessor.web_clone_account())
    return "清理空余额账户任务已创建"
