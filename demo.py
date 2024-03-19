from solana.rpc.api import Client

from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction,

from solders.system_program import CreateAccountParams
from solders.token.associated import get_associated_token_address
from spl.token.async_client import AsyncToken
from spl.token.instructions import InitializeAccountParams


async def swap_on_raydium(wallet_keypair, token_mint_address, token_amount):
    async with AsyncClient('https://api.devnet.solana.com') as client:
        async with AsyncToken(client) as token_client:
            token_account_address = await get_associated_token_address(
                wallet_keypair.public_key,
                token_mint_address
            )

            # Check if the token account exists, if not create it
            try:
                token_account_info = await token_client.get_account_info(token_account_address)
            except:
                create_account_ix = InitializeAccountParams(
                    decimals=0,
                    mint=token_mint_address,
                    program_id=token_client.program_id,
                    mint_authority=wallet_keypair.public_key
                )
                txn = Transaction()
                txn.add(
                    token_client.create_account(
                        CreateAccountParams(
                            from_pubkey=wallet_keypair.public_key,
                            new_account_pubkey=token_account_address,
                            lamports=await token_client.get_min_balance_rent_exemption(
                                CreateAccountParams.get_packed_len()
                            ),
                            space=CreateAccountParams.get_packed_len(),
                            program_id=token_client.program_id
                        ),
                        create_account_ix
                    )
                )
                await client.send_transaction(txn, wallet_keypair)

            # Get the token account balance
            token_account_balance = token_client.parse_token_account_info(
                token_account_info.data
            )

            if token_account_balance < token_amount:
                raise Exception("Insufficient token balance")

            # Swap SOL for the specified token
            swap_ix = async_transfer(
                token_account_address,
                wallet_keypair.public_key,
                token_amount,
                wallet_keypair.public_key,
                token_mint_address
            )
            txn = Transaction()
            txn.add(swap_ix)

            # Sign and send the transaction
            await client.send_transaction(txn, wallet_keypair)

            return txn.signatures

# Example usage
wallet_keypair = Keypair.from_seed(b'your_wallet_seed_bytes')
token_mint_address = PublicKey('your_token_mint_address')
token_amount = 1000000  # 1 SOL in lamports
swap_tx_signatures = await swap_on_raydium(wallet_keypair, token_mint_address, token_amount)
print("Swap transaction signatures:", swap_tx_signatures)