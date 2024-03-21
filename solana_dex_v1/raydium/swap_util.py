from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from spl.token.constants import TOKEN_PROGRAM_ID

from solana_dex_v1.common.constants import RAYDIUM_LIQUIDITY_POOL_V4
from solana_dex_v1.layout.raydium_layout import ROUTE_DATA_LAYOUT
from solana_dex_v1.raydium.models import ApiPoolInfo


def make_swap_instruction(
        amount_in: int,
        token_account_in: Pubkey,
        token_account_out: Pubkey,
        owner: Pubkey,
        pool_info: ApiPoolInfo
) -> Instruction:
    keys = [
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.id, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.openOrders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.targetOrders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.baseVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.quoteVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.baseMint, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.marketId, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketBids, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketAsks, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketEventQueue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketBaseVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketQuoteVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketAuthority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=token_account_in, is_signer=False, is_writable=True),  # UserSourceTokenAccount
        AccountMeta(pubkey=token_account_out, is_signer=False, is_writable=True),  # UserDestTokenAccount
        AccountMeta(pubkey=owner, is_signer=True, is_writable=False)  # UserOwner
    ]

    data = ROUTE_DATA_LAYOUT.build(
        dict(
            instruction=9,
            amount_in=int(amount_in),
            min_amount_out=0
        )
    )
    return Instruction(RAYDIUM_LIQUIDITY_POOL_V4, data, keys)
