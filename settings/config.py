import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PRIVATE_KEY: str
    RPC_ENDPOINT: str = ""
    RPC_WEBSOCKET_ENDPOINT: str = ""
    USE_SNIPE_LIST: bool = False
    MAX_BUY_RETRIES: int = 1
    MAX_SELL_RETRIES: int = 5
    MICROLAMPORTS: int = 250000
    AUTO_SELL_STATUS: bool = False
    AUTO_SELL_TIME: int = 60
    WEB_PORT: int = 5000
    JITO_ENGINE: str = "tokyo.mainnet.block-engine.jito.wtf"
    JITO_STATUS: bool = False
    JITO_BUY_TIP_AMOUNT: float = 0.00001
    JITO_SELL_TIP_AMOUNT: float = 0.00001
    REDIS_URL: str = "redis://127.0.0.1:6379"
    OPENBOOK_STATUS: bool = False

    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')


AppConfig = Config()
