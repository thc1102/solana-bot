from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PRIVATE_KEY: str
    RPC_ENDPOINT: str = ""
    RPC_WEBSOCKET_ENDPOINT: str = ""
    USE_SNIPE_LIST: bool = False
    MAX_BUY_RETRIES: int = 2
    MAX_SELL_RETRIES: int = 5
    MICROLAMPORTS: int = 250000
    AUTO_TRADING: bool = False
    AUTO_QUOTE_AMOUNT: float = 0.01
    AUTO_SELL_STATUS: bool = False
    CHECK_IF_MINT_IS_RENOUNCED: bool = False
    POOL_SIZE: int = 1000
    AUTO_SELL_TIME: int = 60
    RUN_LP_TIME: int = 60

    class Config:
        env_file = '.env'


AppConfig = Config()
