from tortoise import fields
from tortoise.models import Model

from solana_dex.raydium.models import MinimalMarketState


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
    updatedAt = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "raydium_pool"


class MarketState(Model):
    baseMint = fields.CharField(max_length=50)
    eventQueue = fields.CharField(max_length=50)
    bids = fields.CharField(max_length=50)
    asks = fields.CharField(max_length=50)
    baseVault = fields.CharField(max_length=50)
    quoteVault = fields.CharField(max_length=50)
    vaultSignerNonce = fields.IntField()

    class Meta:
        table = "market_state"

    def to_str(self):
        return f"eventQueue {self.eventQueue} bids {self.bids} asks {self.asks}"

    def to_model(self):
        return MinimalMarketState(
            self.eventQueue,
            self.bids,
            self.asks,
            self.vaultSignerNonce,
            self.baseVault,
            self.quoteVault
        )
