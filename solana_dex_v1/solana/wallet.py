from typing import Optional

from solana.rpc.commitment import Commitment
from solana.rpc.types import TokenAccountOpts
from solders.keypair import Keypair

from solana_dex_v1.common.constants import TOKEN_PROGRAM_ID
from solana_dex_v1.solana.solana_client import SolanaRPCClient


class Wallet:
    def __init__(self, keypair: str):
        self.keypair = Keypair.from_base58_string(keypair)
        self.pubkey = self.keypair.pubkey()

    def get_pubkey(self):
        return self.pubkey

    def get_keypair(self):
        return self.keypair

    async def get_sol_balance(self):
        """
        获取钱包中 SOL 的余额。

        返回:
            float: SOL 余额。
        """
        balance_resp = await SolanaRPCClient.get_balance(self.pubkey)
        return balance_resp.value / 10 ** 9

    async def get_token_accounts(self, commitment: Optional[Commitment] = None):
        """
        异步函数：获取当前钱包的代币账户
        Args:
            commitment (Commitment, optional): 事务提交选项，默认为None
        Returns:
            list: 令牌账户列表
        """

        balance = await SolanaRPCClient.get_token_accounts_by_owner_json_parsed(self.pubkey,
                                                                                TokenAccountOpts(
                                                                                    program_id=TOKEN_PROGRAM_ID),
                                                                                commitment)
        print(balance)
        for i in balance.value:
            print(i)
            print(i.account.data.parsed.get("info").get("mint"),
                  i.account.data.parsed.get("info").get("tokenAmount").get("uiAmount"))
