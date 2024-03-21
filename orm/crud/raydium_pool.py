from orm.models.raydium_pool import RaydiumPool


class RaydiumPoolHelper:
    @staticmethod
    async def bulk_create_pools(data_list):
        pools = await RaydiumPool.bulk_create([RaydiumPool(**data) for data in data_list])
        return pools

    @staticmethod
    async def create_pool(data):
        pool = await RaydiumPool.create(**data)
        return pool

    @staticmethod
    async def get_pool(pool_id):
        pool = await RaydiumPool.get_or_none(id=pool_id)
        return pool

    @staticmethod
    async def update_pool(pool_id, data):
        await RaydiumPool.filter(id=pool_id).update(**data)

    @staticmethod
    async def delete_pool(pool_id):
        await RaydiumPool.filter(id=pool_id).delete()

    @staticmethod
    async def get_pool_by_mint(base_mint):
        pool = await RaydiumPool.filter(baseMint=base_mint)
        return pool

    @staticmethod
    async def get_pool_count():
        pool_count = await RaydiumPool.all().count()
        return pool_count
