import asyncio

from solana import transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Finalized, Processed
from solana.transaction import Transaction, NonceInformation
from solders._system_program import create_nonce_account
from solders.account import Account
from solders.hash import Hash
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.system_program import initialize_nonce_account, InitializeNonceAccountParams, transfer, TransferParams, \
    advance_nonce_account, AdvanceNonceAccountParams
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import initialize_account, InitializeAccountParams

from settings.config import AppConfig
from solana_dex.common.constants import LAMPORTS_PER_SOL, SOL_MINT_ADDRESS
from solana_dex.swap.wallet import Wallet
from utils.client_utils import AsyncClientFactory


# from solana.account import Account
# from solana.rpc.api import Client
# from solana.system_program import create_nonce_account
# from solana.transaction import Transaction
#
# # Create connection
# rpc_url = 'https://api.devnet.solana.com'  # Devnet RPC URL
# client = Client(rpc_url)


#
# # Generate accounts
# account = Account()
# nonce_account = Account()
#
# # Fund account
# client.request_airdrop(account.public_key(), 1_000_000_000)  # Request airdrop
#
# # Get minimum amount for rent exemption
# minimum_rent_balance = client.get_minimum_balance_for_rent_exemption(96)  # Nonce account length
#
# # Form CreateNonceAccount transaction
# create_nonce_tx = Transaction().add(
#     create_nonce_account(
#         from_pubkey=account.public_key(),
#         nonce_pubkey=nonce_account.public_key(),
#         authorized_pubkey=account.public_key(),
#         lamports=minimum_rent_balance,
#     )
# )
#
# # Sign transaction
# create_nonce_tx.sign(account)
# create_nonce_tx.sign(nonce_account)
#
# # Send transaction
# tx_sig = client.send_transaction(create_nonce_tx, account, nonce_account)
#
# # Confirm transaction
# client.confirm_transaction(tx_sig)
#
# # Get nonce account information
# nonce_account_info = client.get_account_info(nonce_account.public_key())
# print(nonce_account_info)

async def test():
    async with AsyncClientFactory() as client:
        my_account = Keypair.from_base58_string(AppConfig.PRIVATE_KEY)
        nonce_account = Keypair.from_base58_string(
            "3SGrJZG2RQX5uLyLKGAwYkDHdurvyHhhXu1oj1RMdHkoocxTxGXpcbnuMB19Dgf47NXcuCLjyoDihckn5dzbmMwP")
        print(f"您的账户私钥 {my_account}")
        print(f"nonce账户私钥 {nonce_account} {nonce_account.pubkey()}")
        # minimum_rent_balance = (await client.get_minimum_balance_for_rent_exemption(96)).value
        # blockhash = (await client.get_latest_blockhash(Processed)).value.blockhash
        # instructions = create_nonce_account(
        #     from_pubkey=my_account.pubkey(),
        #     nonce_pubkey=nonce_account.pubkey(),
        #     authority=my_account.pubkey(),
        #     lamports=int(minimum_rent_balance),
        # )
        # create_nonce_tx = Transaction(blockhash, fee_payer=my_account.pubkey(), instructions=instructions)
        # create_nonce_tx.sign(my_account, nonce_account)
        # txn_signature = create_nonce_tx.signatures[0]
        # print(txn_signature)
        # await client.send_transaction(create_nonce_tx, my_account, nonce_account)
        # await client.confirm_transaction(txn_signature)
        data = await client.get_account_info_json_parsed(nonce_account.pubkey())
        authority = data.value.data.parsed.get("info").get("authority")
        blockhash = data.value.data.parsed.get("info").get("blockhash")
        print("authority", authority)
        print("blockhash", blockhash)
        instructions = [transfer(
            TransferParams(from_pubkey=my_account.pubkey(),
                           to_pubkey=nonce_account.pubkey(),
                           lamports=10000,
                           )
        )]
        nonce_info = NonceInformation(nonce=Hash.from_string(blockhash),
                                      nonce_instruction=advance_nonce_account(
                                          AdvanceNonceAccountParams(authorized_pubkey=my_account.pubkey(),
                                                                    nonce_pubkey=nonce_account.pubkey())))

        print(nonce_info)
        tx = Transaction(nonce_info=nonce_info, fee_payer=my_account.pubkey(), instructions=instructions)
        tx.sign(my_account)
        print(await client.simulate_transaction(tx))


if __name__ == '__main__':
    print(Pubkey.default().LENGTH)
    asyncio.run(test())
