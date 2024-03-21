from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from get_pool_strings import gen_pool as gen_pool_strings
from get_pool_public_keys import gen_pool as gen_pool_public_keys
import asyncio

RPC_HTTPS_URL = "https://dimensional-frequent-wave.solana-mainnet.quiknode.pro/ab01b5056e35be398d8fa71f3d305c7848bf23fb/"


async def test():
    amm_id = "481zvrYvFh9jiGBgxj3PZ7rNAFkKtagoGeLoWPJC9xG6"  # test

    ctx = AsyncClient(RPC_HTTPS_URL, commitment=Confirmed)

    keys_in_the_form_strings = await gen_pool_strings(amm_id, ctx)
    print(keys_in_the_form_strings)

    print("*" * 500)

    keys_in_the_form_of_public_keys = await gen_pool_public_keys(amm_id, ctx)
    print(keys_in_the_form_of_public_keys)


asyncio.run(test())
