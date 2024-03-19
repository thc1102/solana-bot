from decimal import Decimal

from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.rpc.errors import InvalidParamsMessage
from solders.token.associated import get_associated_token_address

import solana_dex.solana.client_wrapper as client_wrapper
from solana_dex.raydium_pool import RaydiumPool


class Wallet:
    def __init__(self, client: AsyncClient, payer: Pubkey):
        """
        初始化钱包对象。

        参数:
            client (Client): Solana RPC 客户端。
            payer (Pubkey): 钱包所有者的 Solana 公钥。
        """
        self.client = client
        self.payer = payer

    async def get_balance(self, pool: RaydiumPool, commitment: str = "confirmed"):
        """
        获取钱包在指定池中的代币余额。

        参数:
            pool (RaydiumPool): Raydium 池对象。
            commitment (str): 事务确认级别，默认为 "confirmed"。

        返回:
            tuple: 代币余额和代币数量。
        """
        address = get_associated_token_address(self.payer, pool.get_mint_address())
        balance_resp = await client_wrapper.get_token_account_balance(
            self.client, address, commitment
        )
        if isinstance(balance_resp, InvalidParamsMessage):
            return 0
        return (
            float(balance_resp.value.amount) / 10 ** int(balance_resp.value.decimals),
            int(balance_resp.value.amount),
        )

    async def get_sol_balance(self):
        """
        获取钱包中 SOL 的余额。

        返回:
            float: SOL 余额。
        """
        balance_resp = await client_wrapper.get_balance(self.client, self.payer)
        return balance_resp.value / 10 ** 9
