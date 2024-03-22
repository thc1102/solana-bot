from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.keypair import Keypair
from solders.pubkey import Pubkey


def convert_lamports_to_sol(lamports):
    # 假设代币用9个小数点表示
    return lamports / 1e9

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
    wallet = Wallet("2CpVUWrFP51Njq441oJAbe2dLcSPMhXkcc2Wu1GVfVQ5vaHp8c5SQ8mS4AXKdv4FTpQAyb7mnQW3zsR1ReZyX8s")
    # 创建Solana RPC客户端
    client = Client(rpc_url)

    token_accounts = client.get_balance(
        wallet.get_wallet_pubkey()
    )
    print(convert_lamports_to_sol(token_accounts.value))

    # 获取钱包地址对应的wSOL代币余额
    try:
        balance = client.get_token_accounts_by_owner(wallet.get_wallet_pubkey(), TokenAccountOpts(
            program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")))
        print("钱包地址:", wallet.get_wallet_pubkey())
        print(len(balance.value))
        for i in balance.value:
            data = SPL_ACCOUNT_LAYOUT.parse(i.account.data)
            print(data)
    except RpcResponseError as e:
        print("无法获取wSOL余额:", e)

