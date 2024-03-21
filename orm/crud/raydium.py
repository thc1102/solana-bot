from orm.models.raydium import RaydiumPool, MarketState


async def bulk_create_pools(data_list):
    pools = await RaydiumPool.bulk_create([RaydiumPool(**data) for data in data_list])
    return pools


async def create_pool(data):
    pool = await RaydiumPool.create(**data)
    return pool


async def get_pool(pool_id):
    pool = await RaydiumPool.get_or_none(id=pool_id)
    return pool


async def update_pool(pool_id, data):
    await RaydiumPool.filter(id=pool_id).update(**data)


async def delete_pool(pool_id):
    await RaydiumPool.filter(id=pool_id).delete()


async def get_pool_by_mint(base_mint):
    pool = await RaydiumPool.filter(baseMint=base_mint)
    return pool


async def get_pool_count():
    pool_count = await RaydiumPool.all().count()
    return pool_count


async def create_market_state(data):
    market_state = await MarketState.filter(baseMint=data.get("baseMint"))
    if len(market_state) != 0:
        await update_market_state(data.get("baseMint"), data)
        return data
    market_state = await MarketState.create(**data)
    return market_state


async def get_market_state(base_mint):
    market_state = await MarketState.filter(baseMint=base_mint).first()
    return market_state


async def update_market_state(base_mint, data):
    await MarketState.filter(baseMint=base_mint).update(**data)
