from solders.pubkey import Pubkey

from solana_dex.common.constants import OPENBOOK_MARKET, RAYDIUM_LIQUIDITY_POOL_V4, \
    RAYDIUM_AMM_AUTHORITY
from solana_dex.layout.market import MARKET_STATE_LAYOUT_V3
from utils.liquidity_utils import get_associated_id, get_associated_open_orders, get_associated_target_orders, \
    get_associated_base_vault, get_associated_quote_vault, get_associated_lp_mint


class PoolInfo:
    def __init__(self, data):
        self.id = None
        self.baseMint = None
        self.authority = None
        self.openOrders = None
        self.targetOrders = None
        self.baseVault = None
        self.quoteVault = None
        self.marketId = None
        self.marketBids = None
        self.marketAsks = None
        self.marketEventQueue = None
        self.marketBaseVault = None
        self.marketQuoteVault = None
        self.marketAuthority = None
        for key, value in data.items():
            setattr(self, key, value)

    @classmethod
    def from_market(cls, market: MARKET_STATE_LAYOUT_V3):
        data = {
            "id": get_associated_id(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress),
            "baseMint": market.baseMint,
            "quoteMint": market.quoteMint,
            "authority": RAYDIUM_AMM_AUTHORITY,
            "openOrders": get_associated_open_orders(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress),
            "targetOrders": get_associated_target_orders(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress),
            "baseVault": get_associated_base_vault(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress),
            "quoteVault": get_associated_quote_vault(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress),
            "marketId": market.ownAddress,
            "marketBids": market.bids,
            "marketAsks": market.asks,
            "marketBaseVault": market.baseVault,
            "marketQuoteVault": market.quoteVault,
            "marketAuthority": Pubkey.create_program_address(
                [bytes(market.ownAddress), bytes([market.vaultSignerNonce]), bytes(7)],
                OPENBOOK_MARKET,
            ),
            "marketEventQueue": market.eventQueue
        }
        return cls(data)

    @classmethod
    def from_json(cls, data: dict):
        data = {key: Pubkey.from_string(value) for key, value in data.items()}
        return cls(data)

    def to_json(self):
        return {key: str(getattr(self, key)) for key in vars(self)}
