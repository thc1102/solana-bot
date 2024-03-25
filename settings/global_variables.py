import asyncio

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from settings.config import AppConfig


class GlobalVariables:
    SolaraClient = AsyncClient(endpoint=AppConfig.RPC_ENDPOINT, commitment=Confirmed, blockhash_cache=True)
    stop_event = asyncio.Event()
    default_wallet = None
