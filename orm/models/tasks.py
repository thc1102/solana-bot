from tortoise import Model, fields


class Tasks(Model):
    id = fields.IntField(pk=True)
    baseMint = fields.CharField(max_length=50)
    amount = fields.FloatField()
    updatedAt = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"


class TasksLog(Model):
    pubkey = fields.CharField(max_length=50)
    baseMint = fields.CharField(max_length=50)
    tx = fields.CharField(max_length=255)
    amount = fields.IntField()
    status = fields.CharField(max_length=50)
    result = fields.CharField(max_length=255)
    updatedAt = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks_log"
