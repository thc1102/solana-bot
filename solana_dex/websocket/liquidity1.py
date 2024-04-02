import asyncio

import websockets
from asyncstdlib import enumerate
from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Confirmed
from solana.rpc.websocket_api import connect
from solders.pubkey import Pubkey
from solders.rpc.config import RpcTransactionLogsFilterMentions

# from solana_dex.tasks_processor import TasksProcessor

solana_client = AsyncClient(
    "https://aged-few-sailboat.solana-mainnet.quiknode.pro/a59a384a0e707c877100881079c24ebfee00eb1b/")


async def parse_liqudity_data(data):
    try:
        if not data.result.value.err:
            logger.info(data.result.value)
            # logger.info((await solana_client.get_transaction(data.result.value.signature, commitment=Confirmed,
            #                                                  max_supported_transaction_version=2)))
        # await TasksProcessor.liqudity_tasks(str(data.result.value.pubkey), liqudity_info)
    except Exception as e:
        logger.error(e)


async def run():
    logger.info("监听 Raydium 变化")
    while True:
        try:
            async with connect(
                    "wss://aged-few-sailboat.solana-mainnet.quiknode.pro/a59a384a0e707c877100881079c24ebfee00eb1b/") as wss:
                await wss.program_subscribe(
                    Pubkey.from_string("7YttLkHDoNj9wyDur5pM1ejNaAvT9X4eqaYcHQqtj2G5"), Processed
                    # data_slice=DataSliceOpts(length=752, offset=0),
                    # filters=[
                    #     MemcmpOpts(offset=432, bytes="So11111111111111111111111111111111111111112"),
                    #     MemcmpOpts(offset=560, bytes="srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"),
                    # ]
                )
                first_resp = await wss.recv()
                subscription_id = first_resp[0].result
                async for idx, updated_info in enumerate(wss):
                    asyncio.create_task(parse_liqudity_data(updated_info[0]))
                await wss.program_unsubscribe(subscription_id)
        except (ConnectionResetError, websockets.exceptions.ConnectionClosedError) as e:
            logger.error(f"发生错误 {e} 正在重试...")
            continue
        except Exception as e:
            logger.error(f"发生意外错误 {e}")


asyncio.run(run())
