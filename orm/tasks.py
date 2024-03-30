from tortoise import Model, fields


class Tasks(Model):
    id = fields.IntField(pk=True)
    baseMint = fields.CharField(max_length=50)
    amount = fields.FloatField()
    status = fields.IntField(default=0)
    updatedAt = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks"


class TasksLog(Model):
    pubkey = fields.CharField(max_length=50)
    baseMint = fields.CharField(max_length=50)
    tx = fields.CharField(max_length=255, default="")
    amount = fields.CharField(max_length=255, default="")
    msg = fields.CharField(max_length=50)
    status = fields.IntField()
    result = fields.CharField(max_length=255, default="")
    updatedAt = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "tasks_log"
