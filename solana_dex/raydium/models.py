from solders.pubkey import Pubkey
from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4, RAY_AUTHORITY_V4
from solana_dex.layout.raydium_layout import LIQUIDITY_STATE_LAYOUT_V4


class MinimalMarketState:
    def __init__(
            self,
            event_queue: str,
            bids: str,
            asks: str,
            vault_signer_nonce: int,
            base_vault: str,
            quote_vault: str

    ):
        self.eventQueue = Pubkey.from_string(event_queue)
        self.bids = Pubkey.from_string(bids)
        self.asks = Pubkey.from_string(asks)
        self.vaultSignerNonce = vault_signer_nonce
        self.baseVault = Pubkey.from_string(base_vault)
        self.quoteVault = Pubkey.from_string(quote_vault)


class ApiPoolInfo:
    def __init__(
            self,
            amm_id: Pubkey,
            liquidity_pool: LIQUIDITY_STATE_LAYOUT_V4,
            market_state: MinimalMarketState
    ):
        self.id = amm_id
        self.baseMint = liquidity_pool.baseMint
        self.quoteMint = liquidity_pool.quoteMint
        self.lpMint = liquidity_pool.lpMint
        self.baseDecimals = liquidity_pool.baseDecimal
        self.quoteDecimals = liquidity_pool.quoteDecimal
        self.lpDecimals = 5
        self.version = 4
        self.programId = RAYDIUM_LIQUIDITY_POOL_V4
        self.authority = RAY_AUTHORITY_V4
        self.openOrders = liquidity_pool.openOrders
        self.targetOrders = liquidity_pool.targetOrders
        self.baseVault = liquidity_pool.baseVault
        self.quoteVault = liquidity_pool.quoteVault
        self.withdrawQueue = liquidity_pool.withdrawQueue
        self.lpVault = liquidity_pool.lpVault
        self.marketVersion = 3
        self.marketProgramId = liquidity_pool.marketProgramId
        self.marketId = liquidity_pool.marketId
        self.marketAuthority = Pubkey.create_program_address(
            [bytes(liquidity_pool.marketId)]
            + [bytes([market_state.vaultSignerNonce])]
            + [bytes(7)],
            liquidity_pool.marketProgramId,
        )
        self.marketBaseVault = market_state.baseVault
        self.marketQuoteVault = market_state.quoteVault
        self.marketBids = market_state.bids
        self.marketAsks = market_state.asks
        self.marketEventQueue = market_state.eventQueue
        self.lookupTableAccount = Pubkey.default()

    def to_dict(self):
        return {
            'id': self.id,
            'baseMint': self.baseMint,
            'quoteMint': self.quoteMint,
            'lpMint': self.lpMint,
            'baseDecimals': self.baseDecimals,
            'quoteDecimals': self.quoteDecimals,
            'lpDecimals': self.lpDecimals,
            'version': self.version,
            'programId': self.programId,
            'authority': self.authority,
            'openOrders': self.openOrders,
            'targetOrders': self.targetOrders,
            'baseVault': self.baseVault,
            'quoteVault': self.quoteVault,
            'withdrawQueue': self.withdrawQueue,
            'lpVault': self.lpVault,
            'marketVersion': self.marketVersion,
            'marketProgramId': self.marketProgramId,
            'marketId': self.marketId,
            'marketAuthority': self.marketAuthority,
            'marketBaseVault': self.marketBaseVault,
            'marketQuoteVault': self.marketQuoteVault,
            'marketBids': self.marketBids,
            'marketAsks': self.marketAsks,
            'marketEventQueue': self.marketEventQueue,
            'lookupTableAccount': self.lookupTableAccount,
        }

    def __str__(self):
        return (
            f"ApiPoolInfo:\n"
            f"  id: {self.id}\n"
            f"  baseMint: {self.baseMint}\n"
            f"  quoteMint: {self.quoteMint}\n"
            f"  lpMint: {self.lpMint}\n"
            f"  baseDecimals: {self.baseDecimals}\n"
            f"  quoteDecimals: {self.quoteDecimals}\n"
            f"  lpDecimals: {self.lpDecimals}\n"
            f"  version: {self.version}\n"
            f"  programId: {self.programId}\n"
            f"  authority: {self.authority}\n"
            f"  openOrders: {self.openOrders}\n"
            f"  targetOrders: {self.targetOrders}\n"
            f"  baseVault: {self.baseVault}\n"
            f"  quoteVault: {self.quoteVault}\n"
            f"  withdrawQueue: {self.withdrawQueue}\n"
            f"  lpVault: {self.lpVault}\n"
            f"  marketVersion: {self.marketVersion}\n"
            f"  marketProgramId: {self.marketProgramId}\n"
            f"  marketId: {self.marketId}\n"
            f"  marketAuthority: {self.marketAuthority}\n"
            f"  marketBaseVault: {self.marketBaseVault}\n"
            f"  marketQuoteVault: {self.marketQuoteVault}\n"
            f"  marketBids: {self.marketBids}\n"
            f"  marketAsks: {self.marketAsks}\n"
            f"  marketEventQueue: {self.marketEventQueue}\n"
            f"  lookupTableAccount: {self.lookupTableAccount}\n"
        )


class WebPoolInfo:
    def __init__(
            self,
            data: dict
    ):
        self.id = Pubkey.from_string(data.get("id"))
        self.baseMint = Pubkey.from_string(data.get("baseMint"))
        self.quoteMint = Pubkey.from_string(data.get("quoteMint"))
        self.authority = RAY_AUTHORITY_V4
        self.openOrders = Pubkey.from_string(data.get("openOrders"))
        self.targetOrders = Pubkey.from_string(data.get("targetOrders"))
        self.baseVault = Pubkey.from_string(data.get("baseVault"))
        self.quoteVault = Pubkey.from_string(data.get("quoteVault"))
        self.marketId = Pubkey.from_string(data.get("marketId"))
        self.marketBids = Pubkey.from_string(data.get("marketBids"))
        self.marketAsks = Pubkey.from_string(data.get("marketAsks"))
        self.marketBaseVault = Pubkey.from_string(data.get("marketBaseVault"))
        self.marketQuoteVault = Pubkey.from_string(data.get("marketQuoteVault"))
        self.marketAuthority = Pubkey.from_string(data.get("marketAuthority"))
        self.marketEventQueue = Pubkey.from_string(data.get("marketEventQueue"))
