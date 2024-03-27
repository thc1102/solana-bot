import asyncio

from tortoise import Tortoise

from solana_dex.transaction_processor import TransactionProcessor


async def init_db():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['orm.models.raydium', 'orm.models.tasks']}
    )
    await Tortoise.generate_schemas()


async def test1():
    await init_db()

    await TransactionProcessor.web_sell("FbVPQERfnjaZDHZ7Yspy7uY38gHCkUhcgeCFdLHZyNNA", 1)


if __name__ == '__main__':
    asyncio.run(test1())
