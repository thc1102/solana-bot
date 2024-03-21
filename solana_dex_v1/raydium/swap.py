from solders.transaction import TransactionInstruction
from solders.publickey import PublicKey
from solders.account import AccountMeta
from solana.rpc.types import InstructionType


def make_swap_fixed_in_instruction(
        pool_keys, user_keys, amount_in, min_amount_out, version
):
    LAYOUT = {
        'instruction': 'u8',
        'amountIn': 'u64',
        'minAmountOut': 'u64',
    }
    data = {
        'instruction': 9,
        'amountIn': amount_in,
        'minAmountOut': min_amount_out,
    }
    # Serialize data
    data_buffer = bytes(TransactionInstruction.pack_data(LAYOUT, data))

    keys = [
        # system
        AccountMeta(TOKEN_PROGRAM_ID, False),
        # amm
        AccountMeta(pool_keys.id, False),
        AccountMeta(pool_keys.authority, False),
        AccountMeta(pool_keys.openOrders, False),
    ]

    if version == 4:
        keys.append(AccountMeta(pool_keys.targetOrders, False))

    keys.extend([
        AccountMeta(pool_keys.baseVault, False),
        AccountMeta(pool_keys.quoteVault, False)
    ])

    if version == 5:
        keys.append(AccountMeta(ModelDataPubkey, False))

    keys.extend([
        # serum
        AccountMeta(pool_keys.marketProgramId, False),
        AccountMeta(pool_keys.marketId, False),
        AccountMeta(pool_keys.marketBids, False),
        AccountMeta(pool_keys.marketAsks, False),
        AccountMeta(pool_keys.marketEventQueue, False),
        AccountMeta(pool_keys.marketBaseVault, False),
        AccountMeta(pool_keys.marketQuoteVault, False),
        AccountMeta(pool_keys.marketAuthority, False),
        # user
        AccountMeta(user_keys.tokenAccountIn, False),
        AccountMeta(user_keys.tokenAccountOut, False),
        AccountMeta(user_keys.owner, True),
    ])

    instruction = TransactionInstruction(
        keys=keys,
        program_id=pool_keys.programId,
        data=data_buffer
    )

    return {
        'address': {},
        'innerTransaction': {
            'instructions': [instruction],
            'signers': [],
            'lookupTableAddress': [
                pool_keys.lookupTableAccount] if pool_keys.lookupTableAccount and not pool_keys.lookupTableAccount == PublicKey.default else [],
            'instructionTypes': [InstructionType.ammV4SwapBaseIn if version == 4 else InstructionType.ammV5SwapBaseIn]
        }
    }


class Swap:
    pass
