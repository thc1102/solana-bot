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
    filtered_list = [item for item in data_list if
                     item.get("quoteMint") == "So11111111111111111111111111111111111111112" or item.get("") == "So11111111111111111111111111111111111111112"]
    print(len(filtered_list))
    # print(await RaydiumPoolHelper.get_all_primary_keys())
    await RaydiumPoolHelper.bulk_create_pools(filtered_list)

    print(await RaydiumPoolHelper.get_pool_by_mint("24gG4br5xFBRmxdqpgirtxgcr7BaWoErQfc2uyDp2Qhh1"))
    # Close Tortoise ORM
    await Tortoise.close_connections()


run_async(init())
