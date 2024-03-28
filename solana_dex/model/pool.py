from solders.pubkey import Pubkey

from solana_dex.common.constants import OPENBOOK_MARKET, RAY_AUTHORITY_V4
from solana_dex.layout.raydium import LIQUIDITY_STATE_LAYOUT_V4


class MarketState:
    def __init__(self, data: dict):
        self.baseMint = data.get("baseMint")
        self.eventQueue = data.get("eventQueue")
        self.bids = data.get("bids")
        self.asks = data.get("asks")
        self.baseVault = data.get("baseVault")
        self.quoteVault = data.get("quoteVault")
        self.vaultSignerNonce = data.get("vaultSignerNonce")


class PoolInfo:
    def __init__(self, data: dict):
        self.id = data.get("id")
        self.baseMint = data.get("baseMint")
        self.quoteMint = data.get("quoteMint")
        self.authority = data.get("authority")
        self.openOrders = data.get("openOrders")
        self.targetOrders = data.get("targetOrders")
        self.baseVault = data.get("baseVault")
        self.quoteVault = data.get("quoteVault")
        self.marketId = data.get("marketId")
        self.marketBids = data.get("marketBids")
        self.marketAsks = data.get("marketAsks")
        self.marketBaseVault = data.get("marketBaseVault")
        self.marketQuoteVault = data.get("marketQuoteVault")
        self.marketAuthority = data.get("marketAuthority")
        self.marketEventQueue = data.get("marketEventQueue")
        self.poolOpenTime = data.get("poolOpenTime")

    @classmethod
    def from_liquidity_and_market(cls, pool_id, market_state: MarketState, liquidity_state: LIQUIDITY_STATE_LAYOUT_V4):
        data = {
            "id": pool_id,
            "baseMint": str(Pubkey.from_bytes(liquidity_state.baseMint)),
            "quoteMint": str(Pubkey.from_bytes(liquidity_state.quoteMint)),
            "authority": str(RAY_AUTHORITY_V4),
            "openOrders": str(Pubkey.from_bytes(liquidity_state.openOrders)),
            "targetOrders": str(Pubkey.from_bytes(liquidity_state.targetOrders)),
            "baseVault": str(Pubkey.from_bytes(liquidity_state.baseVault)),
            "quoteVault": str(Pubkey.from_bytes(liquidity_state.quoteVault)),
            "marketId": str(Pubkey.from_bytes(liquidity_state.marketId)),
            "marketBids": str(Pubkey.from_bytes(market_state.bids)),
            "marketAsks": str(Pubkey.from_bytes(market_state.asks)),
            "marketBaseVault": str(Pubkey.from_bytes(market_state.baseVault)),
            "marketQuoteVault": str(Pubkey.from_bytes(market_state.quoteVault)),
            "marketAuthority": str(Pubkey.create_program_address(
                [liquidity_state.marketId]
                + [bytes([market_state.vaultSignerNonce])]
                + [bytes(7)],
                OPENBOOK_MARKET,
            )),
            "marketEventQueue": str(Pubkey.from_bytes(market_state.eventQueue)),
            "poolOpenTime": liquidity_state.poolOpenTime
        }

        return cls(data)
