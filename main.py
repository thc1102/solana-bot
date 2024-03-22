import asyncio

from loguru import logger
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address
from tortoise import Tortoise

from settings.config import Config
from solana_dex_v1.common.constants import SOL_MINT_ADDRESS
from solana_dex_v1.layout.serum_layout import MARKET_STATE_LAYOUT_V3
from solana_dex_v1.solana.solana_client import SolanaRPCClient
from solana_dex_v1.solana.wallet import Wallet
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
get_associated_token_address

async def init_wallet():
    wallet = Wallet(Config.PRIVATE_KEY)
    sol_balance = await wallet.get_sol_balance()
    logger.info(f"当前账户地址 {wallet.get_pubkey()} SOL余额 {sol_balance}")


async def run():
    await init_db()
    await init_wallet()
    stop_event = asyncio.Event()
    asyncio.create_task(openbook.run())
    asyncio.create_task(liquidity.run())
    await stop_event.wait()


if __name__ == '__main__':
    asyncio.run(run())
