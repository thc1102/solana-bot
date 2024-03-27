from construct import Struct

from solana_dex_v1.utils.layout_utils import WideBitsBuilder, blob, publicKey, u64


def account_flags_layout(_property="accountFlags"):
    builder = WideBitsBuilder(_property)
    builder.add_boolean("initialized")
    builder.add_boolean("market")
    builder.add_boolean("openOrders")
    builder.add_boolean("requestQueue")
    builder.add_boolean("eventQueue")
    builder.add_boolean("bids")
    builder.add_boolean("asks")
    return _property / builder.get_layout()


MARKET_STATE_LAYOUT_V3 = Struct(
    blob("none", 5),
    account_flags_layout("accountFlags"),
    publicKey("ownAddress"),
    u64("vaultSignerNonce"),
    publicKey("baseMint"),
    publicKey("quoteMint"),
    publicKey("baseVault"),
    u64("baseDepositsTotal"),
    u64("baseFeesAccrued"),
    publicKey("quoteVault"),
    u64("quoteDepositsTotal"),
    u64("quoteFeesAccrued"),
    u64("quoteDustThreshold"),
    publicKey("requestQueue"),
    publicKey("eventQueue"),
    publicKey("bids"),
    publicKey("asks"),
    u64("baseLotSize"),
    u64("quoteLotSize"),
    u64("feeRateBps"),
    u64("referrerRebatesAccrued"),
    blob("none", 7),
)
