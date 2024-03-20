# load private key
import asyncio
import time

import base58
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.pubkey import Pubkey

from solana_dex.common.direction import Direction
from solana_dex.raydium_pool import RaydiumPool
from solana_dex.solana_util.serum_market_info import get_market_info
from solana_dex.swap import Swap
from solana_dex.wallet import Wallet

keypair = Keypair.from_bytes(
    base58.b58decode("3Sn6Xoruw3sdYrPoorvW9pj3niJKNaHuwU6uV1vxMZASrbdGfDwnjBTcawzg5bCcRJTSes1yvb8NZquVVwakSFFb"))


# configure rpc client


async def run():
    client = AsyncClient("https://mainnet.helius-rpc.com/?api-key=662f50ce-8a1d-4d1d-8d28-ec62db019c7e")
    # wallet = Wallet(client, Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"))
    # print(await wallet.get_sol_balance())
    # for i in range(1):
    #     t = time.time()
    #     pool = RaydiumPool(client, "AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA")
    #     await pool.initialization_task
    #     print(pool.get_price(10.0, Direction.SPEND_BASE_TOKEN))
    #     print(time.time() - t)
    # print("完成")
    pool = RaydiumPool(client, "AVs9TA4nWDzfPJE9gGVNJMVhcQy3V9PGazuz33BfG2RA")
    await pool.initialization_task
    swap = Swap(client, pool)
    print(pool.get_price(10.0, Direction.SPEND_BASE_TOKEN))
    await swap.buy(1.0, 0.1, keypair)
    # await swap.get_pool_lp_locked_ratio(Keypair.from_base58_string(
    #     "3Sn6Xoruw3sdYrPoorvW9pj3niJKNaHuwU6uV1vxMZASrbdGfDwnjBTcawzg5bCcRJTSes1yvb8NZquVVwakSFFb"))
    await asyncio.sleep(10000)


if __name__ == '__main__':
    asyncio.run(run())
