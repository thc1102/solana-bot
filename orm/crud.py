import asyncio
from solders.pubkey import Pubkey

from orm.tasks import Tasks, TasksLog


async def update_task_status(task_id, status: int = 1):
    await Tasks.filter(id=task_id).update(status=status)


async def create_task_log(pubkey: Pubkey, mint: Pubkey, amount: str, msg: str, status: int, _type: int, tx: str = None):
    log_data = {
        "pubkey": pubkey,
        "baseMint": mint,
        "msg": msg,
        "status": status,
        "type": _type,
        "amount": amount,
    }
    if tx:
        log_data["tx"] = tx
    asyncio.create_task(TasksLog.create(**log_data))
