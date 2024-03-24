import time

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey

from get_pool_public_keys import gen_pool as gen_pool_public_keys
import asyncio

RPC_HTTPS_URL = "https://dimensional-frequent-wave.solana-mainnet.quiknode.pro/ab01b5056e35be398d8fa71f3d305c7848bf23fb/"


async def test():
    amm_id = "4LgskeiWMRjoZ32uAE5heMiHLfUXc38a7gnyjs1NWyuB"  # test
    #
    ctx = AsyncClient(RPC_HTTPS_URL, commitment=Confirmed)
    #
    # keys_in_the_form_strings = await gen_pool_strings(amm_id, ctx)
    # print(keys_in_the_form_strings)
    #
    # print("*" * 500)
    sol = Pubkey.from_string("So11111111111111111111111111111111111111112")
    print(await ctx.get_token_accounts_by_owner(Pubkey.from_string("2ma4CyZVxj5oRgepJHGq1FwRM7T6iboeghuRHBRJnNwR"),
                                                TokenAccountOpts(sol)))
    # t= time.time()
    # keys_in_the_form_of_public_keys = await gen_pool_public_keys(amm_id, ctx)
    # print(keys_in_the_form_of_public_keys)
    # print(time.time()-t)


asyncio.run(test())
