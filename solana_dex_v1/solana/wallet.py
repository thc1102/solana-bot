from solders.keypair import Keypair

from solana_dex_v1.solana.solana_client import SolanaRPCClient


class Wallet:
    def __init__(self, keypair: str):
        self.keypair = Keypair.from_base58_string(keypair)
        self.pubkey = self.keypair.pubkey()

    def get_pubkey(self):
        return self.pubkey

    async def get_sol_balance(self):
        """
        获取钱包中 SOL 的余额。

        返回:
            float: SOL 余额。
        """
        balance_resp = await SolanaRPCClient.get_balance(self.pubkey)
        return balance_resp.value / 10 ** 9
