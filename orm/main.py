import json

from tortoise.models import Model
from tortoise import fields, Tortoise, run_async

from orm.crud.raydium_pool import RaydiumPoolHelper
from orm.models.raydium_pool import RaydiumPool
from orm.utils import dict_to_model


async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm.models.raydium_pool']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()

    with open(r"D:\Code\Python\solana-bot\liquidity_mainnet.json", encoding="utf-8") as f:
        data = json.loads(f.read())
    data_list = []
    data_list.extend(data.get("unOfficial"))
    data_list.extend(data.get("official"))
    print(len(data_list))
    # print(await RaydiumPoolHelper.get_all_primary_keys())
    await RaydiumPoolHelper.bulk_create_pools(data_list)

    print(await RaydiumPoolHelper.get_pool_by_mint("FTEB3iG1mJPfk8AwtzH555jftz5qT4AJtz24XHFH2Ekj"))
    # Close Tortoise ORM
    await Tortoise.close_connections()


run_async(init())
