import asyncio

from tortoise import Tortoise

from main import inti_jito_client
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.solana.wallet import Wallet
from solana_dex.transaction_processor import TransactionProcessor


async def run():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm.tasks']}
    )
    await Tortoise.generate_schemas()
    wallet = Wallet(AppConfig.PRIVATE_KEY)
    GlobalVariables.default_wallet = wallet
    await wallet.update_token_accounts()
    await inti_jito_client()
    # await asyncio.sleep(180)
    print(await TransactionProcessor.web_buy("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82", 0.01))
    # amount = wallet.get_token_accounts("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82").uiAmount
    # print(amount)
    # print(await TransactionProcessor.web_sell("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82", amount))
    # puy = await swap.buy(Pubkey.from_string("ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82"), 0.01)
    # await asyncio.sleep(60)

    await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(run())
