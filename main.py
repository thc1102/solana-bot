import asyncio

from loguru import logger
from solders.pubkey import Pubkey
from tortoise import Tortoise

from solana_dex_v1.common.constants import SOL_MINT_ADDRESS
from solana_dex_v1.layout.serum_layout import MARKET_STATE_LAYOUT_V3
from solana_dex_v1.solana.solana_client import SolanaRPCClient
from solana_dex_v1.websocket import openbook, liquidity


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm.models.raydium']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()

    # with open(r"D:\Code\solana-bot\liquidity_mainnet.json", encoding="utf-8") as f:
    #     data = json.loads(f.read())
    # data_list = []
    # data_list.extend(data.get("unOfficial"))
    # data_list.extend(data.get("official"))
    # print(len(data_list))
    # print(await RaydiumPoolHelper.get_all_primary_keys())
    # await RaydiumPoolHelper.bulk_create_pools(data_list)

    # print(await RaydiumPoolHelper.get_pool_by_mint("24gG4br5xFBRmxdqpgirtxgcr7BaWoErQfc2uyDp2Qhh1"))
    # Close Tortoise ORM
    # await Tortoise.close_connections()


async def run():
    await init_db()
    stop_event = asyncio.Event()

    # a = await SolanaRPCClient.get_account_info(Pubkey.from_string("7YttLkHDoNj9wyDur5pM1ejNaAvT9X4eqaYcHQqtj2G5"))
    asyncio.create_task(openbook.run())
    asyncio.create_task(liquidity.run())
    await stop_event.wait()


if __name__ == '__main__':
    asyncio.run(run())
