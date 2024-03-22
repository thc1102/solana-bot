from construct import Struct

from solana_dex_v1.layout.utils import pad, publicKey, u8, u64, u128

ROUTE_DATA_LAYOUT = Struct(u8("instruction"), u64("amountIn"), u64("minAmountOut"))

LIQUIDITY_STATE_LAYOUT_V4 = Struct(
    u64("status"),
    u64("nonce"),
    u64("maxOrder"),
    u64("depth"),
    u64("baseDecimal"),
    u64("quoteDecimal"),
    u64("state"),
    u64("resetFlag"),
    u64("minSize"),
    u64("volMaxCutRatio"),
    u64("amountWaveRatio"),
    u64("baseLotSize"),
    u64("quoteLotSize"),
    u64("minPriceMultiplier"),
    u64("maxPriceMultiplier"),
    u64("systemDecimalValue"),
    u64("minSeparateNumerator"),
    u64("minSeparateDenominator"),
    u64("tradeFeeNumerator"),
    u64("tradeFeeDenominator"),
    u64("pnlNumerator"),
    u64("pnlDenominator"),
    u64("swapFeeNumerator"),
    u64("swapFeeDenominator"),
    u64("baseNeedTakePnl"),
    u64("quoteNeedTakePnl"),
    u64("quoteTotalPnl"),
    u64("baseTotalPnl"),
    u64("poolOpenTime"),
    u64("punishPcAmount"),
    u64("punishCoinAmount"),
    u64("orderbookToInitTime"),
    u128("swapBaseInAmount"),
    u128("swapQuoteOutAmount"),
    u64("swapBase2QuoteFee"),
    u128("swapQuoteInAmount"),
    u128("swapBaseOutAmount"),
    u64("swapQuote2BaseFee"),
    publicKey("baseVault"),
    publicKey("quoteVault"),
    publicKey("baseMint"),
    publicKey("quoteMint"),
    publicKey("lpMint"),
    publicKey("openOrders"),
    publicKey("marketId"),
    publicKey("marketProgramId"),
    publicKey("targetOrders"),
    publicKey("withdrawQueue"),
    publicKey("lpVault"),
    publicKey("owner"),
    u64("lpReserve"),
    pad("padding", 8 * 3),
)
