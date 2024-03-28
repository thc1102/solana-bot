import asyncio


class GlobalVariables:
    stop_event = asyncio.Event()
    default_wallet = None
    snipe_list = {}
