from pydantic_settings import BaseSettings


class Config(BaseSettings):
    PRIVATE_KEY: str
    RPC_ENDPOINT: str = ""
    RPC_WEBSOCKET_ENDPOINT: str = ""

    class Config:
        env_file = '.env'


AppConfig = Config()
