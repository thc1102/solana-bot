from construct import Struct

from solana_dex.utils.layout_utils import pad, publicKey, u8, u64, u128, u32, blob

MINT_LAYOUT = Struct(
    u32('mintAuthorityOption'),
    publicKey('mintAuthority'),
    u64('supply'),
    u8('decimals'),
    u8('isInitialized'),
    u32('freezeAuthorityOption'),
    publicKey('freezeAuthority'),
)
