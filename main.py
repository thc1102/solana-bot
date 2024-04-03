import asyncio
import sys

from jito_searcher_client.generated.searcher_pb2 import GetTipAccountsRequest
from solders.pubkey import Pubkey

from solana_dex.common.constants import SOL_MINT_ADDRESS
from utils.client_utils import JitoClientFactory
from solana_dex.websocket import openbook, liquidity
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
from solana_dex.swap.wallet import Wallet


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm.tasks']}
    )
    await Tortoise.generate_schemas()


async def init_wallet():
    wallet = Wallet(AppConfig.PRIVATE_KEY)
    await wallet.update_token_accounts()
    sol_balance = await wallet.get_sol_balance()
    wsol_balance = wallet.get_token_accounts_balance(SOL_MINT_ADDRESS)
    if wsol_balance is None:
        raise ValueError("Wsol账户未开通 暂时无法使用")
    logger.info(f"当前账户地址 {wallet.pubkey} SOL余额 {sol_balance} Wsol余额 {wsol_balance}")
    GlobalVariables.default_wallet = wallet


async def inti_jito_client():
    jito_client = await JitoClientFactory.get_shared_client(GlobalVariables.default_wallet.keypair)
    response = await jito_client.GetTipAccounts(GetTipAccountsRequest())
    tip_accounts = []
    for account in response.accounts:
        tip_accounts.append(Pubkey.from_string(account))
    GlobalVariables.tip_payment_accounts = tip_accounts.copy()
    logger.info(f"初始化jito客户端完成 已载入{len(response.accounts)}个小费账户")


async def run():
    try:
        # 初始化数据库
        await init_db()
        # 初始化钱包
        await init_wallet()
        if AppConfig.JITO_STATUS:
            # 初始化jito客户端并更新小费账户
            await inti_jito_client()
        if not AppConfig.OPENBOOK_STATUS:
            # 启动websocket监控
            asyncio.create_task(openbook.connect_and_subscribe())
        asyncio.create_task(liquidity.connect_and_subscribe())
        # 初始化狙击列表
        if AppConfig.USE_SNIPE_LIST:
            asyncio.create_task(update_snipe_list())
        await GlobalVariables.stop_event.wait()
    except Exception as e:
        logger.error(e)
    finally:
        # 关闭数据库
        await Tortoise.close_connections()
        sys.exit(0)


if __name__ == '__main__':
    asyncio.run(run())
