from solders.pubkey import Pubkey

from solana_dex.common.constants import OPENBOOK_MARKET, RAY_AUTHORITY_V4, RAYDIUM_LIQUIDITY_POOL_V4, \
    RAYDIUM_AMM_AUTHORITY
from solana_dex.layout.market import MARKET_STATE_LAYOUT_V3
from utils.liquidity_utils import get_associated_id, get_associated_open_orders, get_associated_target_orders


class PoolInfo:
    def __init__(self, market: MARKET_STATE_LAYOUT_V3):
        self.id = get_associated_id(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress)
        self.baseMint = market.baseMint
        self.quoteMint = market.quoteMint
        self.authority = RAYDIUM_AMM_AUTHORITY
        self.openOrders = get_associated_open_orders(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress)
        self.targetOrders = get_associated_target_orders(RAYDIUM_LIQUIDITY_POOL_V4, market.ownAddress)
        self.baseVault = ""
        self.quoteVault = ""
        self.marketId = market.ownAddress
        self.marketBids = market.bids
        self.marketAsks = market.asks
        self.marketBaseVault = market.baseVault
        self.marketQuoteVault = market.quoteVault
        self.marketAuthority = Pubkey.create_program_address(
            [bytes(market.ownAddress)]
            + [bytes([market.vaultSignerNonce])]
            + [bytes(7)],
            OPENBOOK_MARKET,
        )
        self.marketEventQueue = market.eventQueue
