import asyncio

from solana.rpc.commitment import Confirmed
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.transaction import VersionedTransaction
from spl.token.instructions import close_account, CloseAccountParams

from settings.global_variables import GlobalVariables
from solana_dex.common.constants import TOKEN_PROGRAM_ID, LAMPORTS_PER_SOL
from solana_dex.layout.solana_layout import MINT_LAYOUT
from solana_dex.solana.solana_client import SolanaRPCClient
from solana_dex.solana.wallet import Wallet
import solders.system_program as sp


async def test1():
    l = ""
    wallet = Wallet("2CpVUWrFP51Njq441oJAbe2dLcSPMhXkcc2Wu1GVfVQ5vaHp8c5SQ8mS4AXKdv4FTpQAyb7mnQW3zsR1ReZyX8s")
    await wallet.update_token_accounts()
    for i, v in wallet.token_data.items():
        print(i, v.address, v.amount)
    try:
        recent_blockhash = GlobalVariables.SolaraClient.blockhash_cache.get()
    except:
        recent_blockhash = (await GlobalVariables.SolaraClient.get_latest_blockhash()).value
    instructions = []
    instructions.append(close_account(
        CloseAccountParams(
            account=Pubkey.from_string("48rtm71FwApU8ZnZHztUKnf3g5hziFtA3pU7GEQwvjtt"),
            dest=wallet.pubkey,
            owner=wallet.pubkey,
            program_id=TOKEN_PROGRAM_ID,
        )
    ))
    compiled_message = MessageV0.try_compile(
        wallet.pubkey,
        instructions,
        [],  # lookup tables
        recent_blockhash.blockhash,
    )
    keypairs = [wallet.keypair]
    transaction = VersionedTransaction(compiled_message, keypairs)
    txn_signature = (await GlobalVariables.SolaraClient.send_transaction(transaction)).value
    print("开始发送", txn_signature)
    resp = await SolanaRPCClient.confirm_transaction(
        txn_signature,
        Confirmed,
    )
    print("等待结果", txn_signature)


if __name__ == '__main__':
    asyncio.run(test1())
