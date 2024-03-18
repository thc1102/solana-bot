from construct import Struct, Int64ul, Padding, Bytes, Adapter
from solders.pubkey import Pubkey


class PublicKeyAdapter(Adapter):
    def _decode(self, obj, context, path):
        # 将字节序列转换为PublicKey对象
        return Pubkey(obj)

    def _encode(self, obj, context, path):
        # 将PublicKey对象转换为字节序列
        return bytes(obj)


# 使用PublicKeyAdapter来创建一个适配器，它处理32字节的数据，并能够在PublicKey对象和字节序列之间转换
def PublicKeyLayout():
    return PublicKeyAdapter(Bytes(32))


# 直接在Struct中使用Bytes(16)定义128位无符号整数字段
LIQUIDITY_STATE_LAYOUT_V4 = Struct(
    "status" / Int64ul,
    "nonce" / Int64ul,
    "maxOrder" / Int64ul,
    "depth" / Int64ul,
    "baseDecimal" / Int64ul,
    "quoteDecimal" / Int64ul,
    "state" / Int64ul,
    "resetFlag" / Int64ul,
    "minSize" / Int64ul,
    "volMaxCutRatio" / Int64ul,
    "amountWaveRatio" / Int64ul,
    "baseLotSize" / Int64ul,
    "quoteLotSize" / Int64ul,
    "minPriceMultiplier" / Int64ul,
    "maxPriceMultiplier" / Int64ul,
    "systemDecimalValue" / Int64ul,
    "minSeparateNumerator" / Int64ul,
    "minSeparateDenominator" / Int64ul,
    "tradeFeeNumerator" / Int64ul,
    "tradeFeeDenominator" / Int64ul,
    "pnlNumerator" / Int64ul,
    "pnlDenominator" / Int64ul,
    "swapFeeNumerator" / Int64ul,
    "swapFeeDenominator" / Int64ul,
    "baseNeedTakePnl" / Int64ul,
    "quoteNeedTakePnl" / Int64ul,
    "quoteTotalPnl" / Int64ul,
    "baseTotalPnl" / Int64ul,
    "poolOpenTime" / Int64ul,
    "punishPcAmount" / Int64ul,
    "punishCoinAmount" / Int64ul,
    "orderbookToInitTime" / Int64ul,
    "swapBaseInAmount" / Bytes(16),
    "swapQuoteOutAmount" / Bytes(16),
    "swapBase2QuoteFee" / Int64ul,
    "swapQuoteInAmount" / Bytes(16),
    "swapBaseOutAmount" / Bytes(16),
    "swapQuote2BaseFee" / Int64ul,
    "baseVault" / PublicKeyLayout(),
    "quoteVault" / PublicKeyLayout(),
    "baseMint" / PublicKeyLayout(),
    "quoteMint" / PublicKeyLayout(),
    "lpMint" / PublicKeyLayout(),
    "openOrders" / PublicKeyLayout(),
    "marketId" / PublicKeyLayout(),
    "marketProgramId" / PublicKeyLayout(),
    "targetOrders" / PublicKeyLayout(),
    "withdrawQueue" / PublicKeyLayout(),
    "lpVault" / PublicKeyLayout(),
    "owner" / PublicKeyLayout(),
    "lpReserve" / Int64ul,
    Padding(24),  # 3个u64的padding，每个u64是8字节
)
