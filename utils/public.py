import asyncio
import datetime
import pickle
from typing import Union, Any
from loguru import logger
from solders.pubkey import Pubkey

from orm.tasks import Tasks
from settings.config import AppConfig
from solana_dex.common.constants import LAMPORTS_PER_SOL
from solana_dex.layout.solana import MINT_LAYOUT
from solana_dex.model.pool import PoolInfo
from solana_dex.utils.client_utils import AsyncClientFactory
from utils.redis_utils import RedisFactory

lock = asyncio.Lock()


async def update_snipe_list():
    # 刷新狙击列表
    all_task = await Tasks.all()
    logger.info(f"狙击列表 当前狙击数量 {len(all_task)}  狙击状态 {AppConfig.USE_SNIPE_LIST}")


async def update_db_pool_data(base_mint, pool_info):
    # 更新redis中池数据
    async with RedisFactory() as r:
        await r.set(f"pool:{base_mint}", pickle.dumps(pool_info))


async def generate_pool_data(base_mint, liqudity_id, liqudity_info):
    # 生成池数据
    async with RedisFactory() as r:
        pool_info = await r.get(f"pool:{base_mint}")
        if pool_info:
            asyncio.create_task(update_db_pool_data(base_mint, pickle.loads(pool_info)))
            return pickle.loads(pool_info)
        market_data = await r.get(f"market:{base_mint}")
        if market_data:
            market_info = pickle.loads(market_data)
            pool_info = PoolInfo.from_liquidity_and_market(liqudity_id, market_info, liqudity_info)
            asyncio.create_task(update_db_pool_data(base_mint, pool_info))
            return pool_info
    return None


async def check_raydium_liquidity(quote_vault: Pubkey):
    # 检测流动池大小
    try:
        async with AsyncClientFactory() as client:
            qvalue = await client.get_balance(quote_vault)
            sol = qvalue.value / LAMPORTS_PER_SOL
            if sol > AppConfig.POOL_SIZE:
                return True
        return False
    except:
        return False


async def check_mint_status(mint: Pubkey):
    # 检测是否停止Mint
    try:
        async with AsyncClientFactory() as client:
            resp = await client.get_account_info(mint)
            mint_info = MINT_LAYOUT.parse(resp.value.data)
            if mint_info.mintAuthorityOption == 0 and mint_info.freezeAuthorityOption == 0:
                return True
            else:
                return False
    except:
        return False

def update_object(obj, data):
    # 更新对象属性值
    for field in obj.__fields__:
        if field in data.__fields__:
            setattr(obj, field, getattr(data, field))


def custom_datetime_serializer(dt: Union[datetime, None]) -> Any:
    # 序列化日期时间
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')
