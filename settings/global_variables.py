import asyncio

from solders.pubkey import Pubkey


class GlobalVariables:
    stop_event = asyncio.Event()
    default_wallet = None
    tip_payment_accounts = [Pubkey.from_string("96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5")]
