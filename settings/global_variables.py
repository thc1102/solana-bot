from solana.rpc.async_api import AsyncClient
from settings.config import AppConfig


class GlobalVariables:
    SolaraClient = AsyncClient(endpoint=AppConfig.RPC_ENDPOINT)
