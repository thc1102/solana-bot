from construct import *
from solders.pubkey import Pubkey


class PublicKeyAdapter(Adapter):
    def _decode(self, obj, context, path):
        # 将字节序列转换为PublicKey对象
        return Pubkey(obj)

    def _encode(self, obj, context, path):
        # 将PublicKey对象转换为字节序列
        return bytes(obj)


def PublicKey():
    return PublicKeyAdapter(Bytes(32))


MARKET_STATE_LAYOUT_V3 = Struct(
    "blob_5" / Bytes(5),
    "account_flags" / Bytes(8),
    "own_address" / PublicKey(),
    "vault_signer_nonce" / Int64ul,
    "base_mint" / PublicKey(),
    "quote_mint" / PublicKey(),
    "base_vault" / PublicKey(),
    "base_deposits_total" / Int64ul,
    "base_fees_accrued" / Int64ul,
    "quote_vault" / PublicKey(),
    "quote_deposits_total" / Int64ul,
    "quote_fees_accrued" / Int64ul,
    "quote_dust_threshold" / Int64ul,
    "request_queue" / PublicKey(),
    "event_queue" / PublicKey(),
    "bids" / PublicKey(),
    "asks" / PublicKey(),
    "base_lot_size" / Int64ul,
    "quote_lot_size" / Int64ul,
    "fee_rate_bps" / Int64ul,
    "referrer_rebates_accrued" / Int64ul,
    "blob_7" / Bytes(7)
)
