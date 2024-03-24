import asyncio
import signal
import sys

from loguru import logger
from solders.pubkey import Pubkey
from spl.token.instructions import get_associated_token_address
from tortoise import Tortoise
from settings.config import AppConfig
from solana_dex.common.constants import SOL_MINT_ADDRESS
from solana_dex.solana.wallet import Wallet
from solana_dex.websocket import openbook, liquidity

from settings.global_variables import GlobalVariables


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm.models.raydium']}
    )
    await Tortoise.generate_schemas()


async def init_wallet():
    wallet = Wallet(AppConfig.PRIVATE_KEY)
    await wallet.update_token_accounts()
    wsol_token = wallet.get_token_accounts(SOL_MINT_ADDRESS)
    if wsol_token is None:
        logger.info("wSOl账户不存在无法使用")
        GlobalVariables.stop_event.set()
        return
    sol_balance = await wallet.get_sol_balance()
    logger.info(f"当前账户地址 {wallet.pubkey} SOL余额 {sol_balance} wSOL余额 {wsol_token.uiAmount}")
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
        # 等待结束指令
        await GlobalVariables.stop_event.wait()
    finally:
        # 关闭数据库
        await Tortoise.close_connections()
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(run())
