from typing import Optional

from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.commitment import Commitment
from solana.rpc.types import TokenAccountOpts
from solders.signature import Signature
from solders.transaction import VersionedTransaction

from settings.global_variables import GlobalVariables


class SolanaRPCClient:

    @staticmethod
    async def get_account_info(address: Pubkey, commitment: Commitment = None):
        """
        异步函数：获取指定地址的账户信息

        Args:
            address (Pubkey): 要查询的账户地址
            commitment (Commitment, optional): 事务提交选项，默认为None

        Returns:
            dict: 指定地址的账户信息
        """
        return await GlobalVariables.SolaraClient.get_account_info(address, commitment)

    @staticmethod
    async def get_balance(address: Pubkey, commitment: Commitment = None):
        """
        异步函数：获取指定地址的余额

        Args:
            address (Pubkey): 要查询的账户地址
            commitment (Commitment, optional): 事务提交选项，默认为None

        Returns:
            float: 指定地址的余额
        """
        return await GlobalVariables.SolaraClient.get_balance(address, commitment)

    @staticmethod
    async def get_token_accounts_by_owner_json_parsed(
            address: Pubkey,
            opts: TokenAccountOpts,
            commitment: Optional[Commitment] = None,
    ):
        """
        异步函数：根据所有者地址获取令牌账户列表
        Args:
            address (Pubkey): 所有者地址
            opts (TokenAccountOpts): 令牌账户选项
            commitment (Commitment, optional): 事务提交选项，默认为None
        Returns:
            list: 令牌账户列表
        """
        return await GlobalVariables.SolaraClient.get_token_accounts_by_owner_json_parsed(address, opts, commitment)

    @staticmethod
    async def get_latest_blockhash():
        """
        异步函数：获取最新的区块哈希

        Returns:
            str: 最新的区块哈希
        """
        try:
            if GlobalVariables.SolaraClient.blockhash_cache:
                recent_blockhash = GlobalVariables.SolaraClient.blockhash_cache.get()
            else:
                recent_blockhash = (await GlobalVariables.SolaraClient.get_latest_blockhash(
                    GlobalVariables.SolaraClient.commitment)).value.blockhash
        except:
            recent_blockhash = (await GlobalVariables.SolaraClient.get_latest_blockhash(
                GlobalVariables.SolaraClient.commitment)).value.blockhash
        return recent_blockhash

    @staticmethod
    async def send_transaction(transaction: VersionedTransaction):
        """
        异步函数：发送交易

        Args:
            transaction (VersionedTransaction): 要发送的交易

        Returns:
            dict: 交易结果
        """
        return await GlobalVariables.SolaraClient.send_transaction(transaction)

    @staticmethod
    async def confirm_transaction(
            txn_signature: Signature,
            commitment: Optional[Commitment] = None,
            sleep_seconds: float = 1,
    ):
        """
        异步函数：确认交易

        Args:
            txn_signature (Signature): 交易签名
            commitment (Commitment): 事务提交选项
            sleep_seconds (float): 等待时间（秒）

        Returns:
            dict: 交易确认结果
        """
        return await GlobalVariables.SolaraClient.confirm_transaction(txn_signature, commitment, sleep_seconds)
