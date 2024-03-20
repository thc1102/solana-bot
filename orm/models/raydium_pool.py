from tortoise import fields
from tortoise.models import Model


class RaydiumPool(Model):
    id = fields.CharField(max_length=100, pk=True)
    baseMint = fields.CharField(max_length=100)
    quoteMint = fields.CharField(max_length=100)
    lpMint = fields.CharField(max_length=100)
    baseDecimals = fields.IntField()
    quoteDecimals = fields.IntField()
    lpDecimals = fields.IntField()
    version = fields.IntField()
    programId = fields.CharField(max_length=100)
    authority = fields.CharField(max_length=100)
    openOrders = fields.CharField(max_length=100)
    targetOrders = fields.CharField(max_length=100)
    baseVault = fields.CharField(max_length=100)
    quoteVault = fields.CharField(max_length=100)
    withdrawQueue = fields.CharField(max_length=100)
    lpVault = fields.CharField(max_length=100)
    marketVersion = fields.IntField()
    marketProgramId = fields.CharField(max_length=100)
    marketId = fields.CharField(max_length=100)
    marketAuthority = fields.CharField(max_length=100)
    marketBaseVault = fields.CharField(max_length=100)
    marketQuoteVault = fields.CharField(max_length=100)
    marketBids = fields.CharField(max_length=100)
    marketAsks = fields.CharField(max_length=100)
    marketEventQueue = fields.CharField(max_length=100)
    lookupTableAccount = fields.CharField(max_length=100, null=True)

    class Meta:
        table = "raydium_pool"
