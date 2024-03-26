import asyncio
import json
import time
from typing import Optional

from loguru import logger
from solana.rpc.commitment import Commitment, Finalized
from solana.rpc.types import TokenAccountOpts
from solders.keypair import Keypair

from solana_dex.common.constants import TOKEN_PROGRAM_ID
from solana_dex.solana.solana_client import SolanaRPCClient

lock = asyncio.Lock()


class TokenAccountData:
    def __init__(self, address, mint, amount, ui_amount):
        # 钱包中的代币地址
        self.address = address
        # 代币的Mint
        self.mint = mint
        # 代币余额
        self.amount = amount
        # 带小数点的余额
        self.uiAmount = ui_amount


class Wallet:
    def __init__(self, keypair: str):
        self.keypair = Keypair.from_base58_string(keypair)
        self.pubkey = self.keypair.pubkey()
        self.token_data = {}

    async def get_sol_balance(self):
        balance_resp = await SolanaRPCClient.get_balance(self.pubkey)
        return balance_resp.value / 10 ** 9

    async def update_token_accounts(self, commitment: Optional[Commitment] = Finalized):
        try:
            balance = await SolanaRPCClient.get_token_accounts_by_owner_json_parsed(self.pubkey,
                                                                                    TokenAccountOpts(
                                                                                        program_id=TOKEN_PROGRAM_ID),
                                                                                    commitment)
            token_data = {}
            for item in balance.value:
                address = item.pubkey
                mint = item.account.data.parsed["info"]["mint"]
                amount = item.account.data.parsed["info"]["tokenAmount"]["amount"]
                ui_amount = item.account.data.parsed["info"]["tokenAmount"]["uiAmount"]
                token_data[mint] = TokenAccountData(address, mint, amount, ui_amount)
            # 加锁保证并发不会影响
            async with lock:
                self.token_data = token_data
        except:
            return False
        return True

    def get_token_accounts(self, mint):
        if not isinstance(mint, str):
            mint = str(mint)
        return self.token_data.get(mint, None)

    def check_token_accounts(self, mint):
        if not isinstance(mint, str):
            mint = str(mint)
        return mint in self.token_data

    def get_no_balance_account(self):
        account_list = []
        for _, data in self.token_data.items():
            if int(data.amount) == 0:
                account_list.append(data.address)
        return account_list
