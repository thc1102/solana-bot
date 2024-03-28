import asyncio
from typing import Union

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Finalized

from settings.config import AppConfig


class AsyncClientFactory:
    def __init__(self, endpoint=AppConfig.RPC_ENDPOINT, commitment=Processed, blockhash_status=False) -> None:
        self.endpoint = endpoint
        self.commitment = commitment
        self.blockhash_status = blockhash_status
        self._client: Union[AsyncClient, None] = None
        self._refresh_task = None
        self._running = False

    async def __aenter__(self) -> "AsyncClient":
        self._client = AsyncClient(endpoint=self.endpoint, commitment=self.commitment,
                                   blockhash_cache=self.blockhash_status)
        if self.blockhash_status:
            self._running = True
            self._refresh_task = asyncio.create_task(self._refresh_blockhash())
        return self._client

    async def __aexit__(self, exc_type, exc, tb):
        if self.blockhash_status:
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
