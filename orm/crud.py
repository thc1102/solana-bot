from orm.tasks import Tasks


async def update_task_status(task_id, status: int = 1):
    await Tasks.filter(id=task_id).update(status=status)
