import asyncio
import sys

from utils.public import update_snipe_list

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except:
    pass

from loguru import logger
from tortoise import Tortoise

from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.solana.wallet import Wallet
from solana_dex.websocket import openbook, liquidity


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm.models.raydium', 'orm.models.tasks']}
    )
    await Tortoise.generate_schemas()


async def init_wallet():
    wallet = Wallet(AppConfig.PRIVATE_KEY)
    await wallet.update_token_accounts()
    sol_balance = await wallet.get_sol_balance()
    logger.info(f"当前账户地址 {wallet.pubkey} SOL余额 {sol_balance}")
    GlobalVariables.default_wallet = wallet


async def run():
    try:
        # 初始化数据库
        await init_db()
        # 初始化钱包
        await init_wallet()
        # 启动websocket监控
        asyncio.create_task(openbook.run())
        asyncio.create_task(liquidity.run())
        # 初始化狙击列表
        asyncio.create_task(update_snipe_list())
        # 等待结束指令
        await GlobalVariables.stop_event.wait()
    finally:
        # 关闭数据库
        await Tortoise.close_connections()
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(run())
