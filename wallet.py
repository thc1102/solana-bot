from solana.rpc.api import Client
from solders.keypair import Keypair
from solders.pubkey import Pubkey


class Wallet:
    def __init__(self, private_key_str):
        self._wallet_keypair = None
        self.set_wallet_keypair(private_key_str)

    def set_wallet_keypair(self, private_key_str):
        self._wallet_keypair = Keypair.from_base58_string(private_key_str)

    def get_wallet_pubkey(self):
        return self._wallet_keypair.pubkey()

    def get_wallet_detail(self):
        pass


class RpcResponseError:
    pass


if __name__ == '__main__':
    rpc_url = 'https://dimensional-frequent-wave.solana-mainnet.quiknode.pro/ab01b5056e35be398d8fa71f3d305c7848bf23fb'
    wallet = Wallet("")
    print(wallet.get_wallet_pubkey())
    wsol_token_address = 'So11111111111111111111111111111111111111112'
    # 创建Solana RPC客户端
    client = Client(rpc_url)

    # 获取wSOL代币的Token ID
    wsol_token_id = Pubkey.from_string(wsol_token_address)
    print(wsol_token_id)
    # 获取钱包地址对应的wSOL代币余额
    try:
        balance = client.get_token_account_balance(wallet.get_wallet_pubkey())
        print("钱包地址:", wallet.get_wallet_pubkey())
        print("SOL余额:", balance)
    except RpcResponseError as e:
        print("无法获取wSOL余额:", e)
