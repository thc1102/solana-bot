from typing import Union

import solders.system_program as sp
import spl.token.instructions as spl_token
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address
from solders.transaction import VersionedTransaction
from spl.token._layouts import ACCOUNT_LAYOUT
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import close_account, CloseAccountParams, create_associated_token_account

from solana_dex_v1.common.constants import OPENBOOK_MARKET, RAYDIUM_LIQUIDITY_POOL_V4
from solana_dex_v1.layout.raydium import ROUTE_DATA_LAYOUT
from solana_dex_v1.model.pool import PoolInfo


def make_swap_instruction(
        amount_in: int,
        token_account_in: Pubkey,
        token_account_out: Pubkey,
        owner: Pubkey,
        pool_info: PoolInfo
) -> Instruction:
    keys = [
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.id, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.openOrders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.targetOrders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.baseVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.quoteVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=OPENBOOK_MARKET, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.marketId, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketBids, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketAsks, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketEventQueue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketBaseVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketQuoteVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketAuthority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=token_account_in, is_signer=False, is_writable=True),
        AccountMeta(pubkey=token_account_out, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=True, is_writable=False)
    ]

    data = ROUTE_DATA_LAYOUT.build(
        dict(
            instruction=9,
            amountIn=int(amount_in),
            minAmountOut=0
        )
    )
    return Instruction(RAYDIUM_LIQUIDITY_POOL_V4, data, keys)
