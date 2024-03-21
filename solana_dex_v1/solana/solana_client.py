import asyncio

from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey

from settings.global_variables import GlobalVariables


class SolanaRPCClient:

    @staticmethod
    async def get_account_info(address: Pubkey, commitment: Commitment = None):
        """
        异步函数：获取指定地址的账户信息

        Args:
            client (AsyncClient): Solana RPC客户端
            address (Pubkey): 要查询的账户地址
            commitment (Commitment, optional): 事务提交选项，默认为None

        Returns:
            dict: 指定地址的账户信息
        """
        return await GlobalVariables.SolaraClient.get_account_info(address, commitment)

