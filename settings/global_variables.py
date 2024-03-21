from solana.rpc.async_api import AsyncClient
from settings.config import Config


class GlobalVariables:
    SolaraClient = AsyncClient(endpoint=Config.RPC_ENDPOINT)
