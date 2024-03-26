import asyncio
import time

import websockets
from loguru import logger
from solana.rpc.commitment import Finalized, Confirmed, Processed
from solana.rpc.types import MemcmpOpts, DataSliceOpts
from solana.rpc.websocket_api import connect
from asyncstdlib import enumerate
from solders.pubkey import Pubkey

from orm.crud.raydium import get_market_state, create_pool
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4, SOL_MINT_ADDRESS, LAMPORTS_PER_SOL
from solana_dex.layout.raydium_layout import LIQUIDITY_STATE_LAYOUT_V4
from solana_dex.layout.solana_layout import MINT_LAYOUT
from solana_dex.raydium.models import ApiPoolInfo
from solana_dex.transaction_processor import TransactionProcessor

exclude_address_set = set()


async def get_market_state_with_retry(base_mint, max_attempts=10):
    attempt = 0
    while attempt < max_attempts:
        market_state = await get_market_state(base_mint)
        if market_state:
            return market_state
        attempt += 1
        await asyncio.sleep(0.2)  # 等待一段时间后重试
    return None


async def check_raydium_liquidity(quote_vault):
    try:
        qvalue = await GlobalVariables.SolaraClient.get_balance(quote_vault)
        sol = qvalue.value / LAMPORTS_PER_SOL
        if sol > AppConfig.POOL_SIZE:
            return True
        else:
            return False
    except:
        return False


async def check_mint_status(mint: Pubkey):
    resp = await GlobalVariables.SolaraClient.get_account_info(mint)
    mint_info = MINT_LAYOUT.parse(resp.value.data)
    if mint_info.mintAuthorityOption == 0 and mint_info.freezeAuthorityOption == 0:
        return True
    else:
        return False


async def parse_liqudity_data(data):
    run_timestamp = time.time()
    try:
        pool_state = LIQUIDITY_STATE_LAYOUT_V4.parse(data.result.value.account.data)
        poolOpenTime = pool_state.poolOpenTime
        if run_timestamp - poolOpenTime < AppConfig.RUN_LP_TIME:
            if pool_state.baseMint in exclude_address_set:
                return
            exclude_address_set.add(pool_state.baseMint)
            market_state = await get_market_state_with_retry(pool_state.baseMint)
            if market_state:
                task_list = []
                logger.info(
                    f"监听到 {pool_state.baseMint} 流动性变化, 运行时间 {round(run_timestamp - poolOpenTime, 3)}, 市场匹配成功")
                pool_info = ApiPoolInfo(data.result.value.pubkey, pool_state, market_state.to_model())
                # 给数据库新增池信息
                asyncio.create_task(create_pool(data.result.value.pubkey, pool_info.to_dict()))
                # 狙击模式优先
                if AppConfig.USE_SNIPE_LIST:
                    tasks_info = GlobalVariables.snipe_list.get(pool_state.baseMint)
                    if tasks_info:
                        asyncio.create_task(TransactionProcessor.append_buy(pool_info, tasks_info))
                        return False
                # 流动池检测
                if AppConfig.POOL_SIZE != 0:
                    task_list.append(check_raydium_liquidity(pool_info.quoteVault))
                # Mint权限检测
                if AppConfig.CHECK_IF_MINT_IS_RENOUNCED:
                    task_list.append(check_mint_status(pool_state.baseMint))
                if len(task_list) != 0:
                    results = await asyncio.gather(*task_list)
                    if any(result is False for result in results):
                        logger.info(f"{pool_state.baseMint} 验证未通过")
                        return False
                if AppConfig.AUTO_TRADING:
                    asyncio.create_task(TransactionProcessor.append_buy(pool_info))
            else:
                logger.warning(
                    f"监听到 {pool_state.baseMint} 流动性变化, 运行时间 {round(run_timestamp - poolOpenTime, 3)}, 市场匹配失败")
                exclude_address_set.discard(pool_state.baseMint)
    except Exception as e:
        logger.info(e)


async def run():
    logger.info("监听 Raydium 变化")
    while True:
        try:
            async with connect(AppConfig.RPC_WEBSOCKET_ENDPOINT, max_queue=None) as wss:
                await wss.program_subscribe(
                    RAYDIUM_LIQUIDITY_POOL_V4, Processed, "base64",
                    data_slice=DataSliceOpts(length=752, offset=0),
                    filters=[
                        MemcmpOpts(offset=432, bytes="So11111111111111111111111111111111111111112"),
                        MemcmpOpts(offset=560, bytes="srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX"),
                        MemcmpOpts(offset=0, bytes="21D35quxec7")
                    ]
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
