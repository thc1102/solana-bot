import asyncio

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed

from settings.config import AppConfig


class GlobalVariables:
    SolaraClient = AsyncClient(endpoint=AppConfig.RPC_ENDPOINT, commitment=Processed, blockhash_cache=True)
    stop_event = asyncio.Event()
    default_wallet = None
    snipe_list = {}
