from orm.models.tasks import Tasks, TasksLog


async def create_tasks(data):
    tasks = await Tasks.create(**data)
    return tasks


async def get_tasks():
    tasks = await Tasks.all()
    return tasks


async def delete_tasks(_id):
    await Tasks.filter(id=_id).delete()


async def create_tasks_log(data):
    tasks_log = await TasksLog.create(**data)
    return tasks_log


async def get_tasks_log():
    tasks_log = await TasksLog.all()
    return tasks_log


async def delete_task_log():
    await TasksLog.all().delete()
