import asyncio

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Finalized


class AsyncClientFactory:
    def __init__(self) -> None:
        self.endpoint = "https://dimensional-frequent-wave.solana-mainnet.quiknode.pro/ab01b5056e35be398d8fa71f3d305c7848bf23fb/"
        self.commitment = Processed
        self._client: [AsyncClient, None] = None
        self._refresh_task = None
        self._running = False

    async def __aenter__(self) -> "AsyncClient":
        self._running = True
        self._client = AsyncClient(endpoint=self.endpoint, commitment=self.commitment,
                                   blockhash_cache=True)
        self._refresh_task = asyncio.create_task(self._refresh_blockhash())
        return self._client

    async def __aexit__(self, exc_type, exc, tb):
        self._running = False
        if self._refresh_task:
            self._refresh_task.cancel()
        return await self._client.close()

    async def _refresh_blockhash(self):
        # 定时刷新blockhash
        while self._running:
            try:
                blockhash_resp = await self._client.get_latest_blockhash(Finalized)
                recent_blockhash = self._client.parse_recent_blockhash(blockhash_resp)
                self._client.blockhash_cache.set(recent_blockhash, blockhash_resp.context.slot, used_immediately=False)
            except Exception as e:
                pass
            finally:
                await asyncio.sleep(60)
