import asyncio
import time

from jito_searcher_client import get_async_searcher_client
from jito_searcher_client.generated.searcher_pb2 import ConnectedLeadersRequest
from solana.rpc.commitment import Processed

from solders.keypair import Keypair

from solana_dex.utils.client_utils import AsyncClientFactory

KEYPAIR = "gGkSP1pa7jWPsBkjiH3zSeTAEjUDCJEUA3FNQuXaDA94SiWeSRgsXbYrUYFGEXmyEP93Q44dmVLoDS9FtjRSWzf"
BLOCK_ENGINE_URL = "frankfurt.mainnet.block-engine.jito.wtf"


async def main():
    for i in range(10):
        t = time.time()
        async with AsyncClientFactory() as rpc_client:
            blockhash = (await rpc_client.get_latest_blockhash()).value.blockhash
            block_height = (await rpc_client.get_block_height(Processed)).value
            print(f"耗时 {time.time() - t}")
            print(f"{blockhash} {block_height}")
        await asyncio.sleep(0.1)


asyncio.run(main())
