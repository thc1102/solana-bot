import asyncio
from typing import Union

from jito_searcher_client import get_async_searcher_client
from jito_searcher_client.generated.searcher_pb2_grpc import SearcherServiceStub
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Finalized, Confirmed
from solders.keypair import Keypair

from settings.config import AppConfig


class AsyncClientFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, endpoint=AppConfig.RPC_ENDPOINT, commitment=Processed) -> None:
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.endpoint = endpoint
            self.commitment = commitment
            self._client: Union[AsyncClient, None] = None

    async def __aenter__(self) -> "AsyncClient":
        if self._client is None:
            self._client = AsyncClient(endpoint=self.endpoint, commitment=self.commitment)
        return self._client

    async def __aexit__(self, exc_type, exc, tb):
        # 关闭上下文不处理
        pass


class JitoClientFactory:
    _shared_client: Union[SearcherServiceStub, None] = None

    @classmethod
    async def get_shared_client(cls, kp: Keypair) -> SearcherServiceStub:
        if cls._shared_client is None:
            cls._shared_client = await get_async_searcher_client(AppConfig.JITO_ENGINE, kp)
        return cls._shared_client

    @classmethod
    async def close_shared_client(cls):
        if cls._shared_client is not None:
            # 关闭客户端连接等操作
            cls._shared_client = None
