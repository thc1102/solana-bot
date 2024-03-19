from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey
from solders.signature import Signature
from solders.transaction import VersionedTransaction


async def get_token_account_balance(
        client: AsyncClient, address: Pubkey, commitment: Commitment = None
):
    """
    异步函数：获取指定地址的令牌账户余额

    Args:
        client (AsyncClient): Solana RPC客户端
        address (Pubkey): 要查询的账户地址
        commitment (Commitment, optional): 事务提交选项，默认为None

    Returns:
        float: 指定地址的令牌账户余额
    """
    return await client.get_token_account_balance(address, commitment)


async def get_balance(client: AsyncClient, address: Pubkey, commitment: Commitment = None):
    """
    异步函数：获取指定地址的余额

    Args:
        client (AsyncClient): Solana RPC客户端
        address (Pubkey): 要查询的账户地址
        commitment (Commitment, optional): 事务提交选项，默认为None

    Returns:
        float: 指定地址的余额
    """
    return await client.get_balance(address, commitment)


async def get_account_info(client: AsyncClient, address: Pubkey, commitment: Commitment = None):
    """
    异步函数：获取指定地址的账户信息

    Args:
        client (AsyncClient): Solana RPC客户端
        address (Pubkey): 要查询的账户地址
        commitment (Commitment, optional): 事务提交选项，默认为None

    Returns:
        dict: 指定地址的账户信息
    """
    return await client.get_account_info(address, commitment)


async def get_account_info_json_parsed(
        client: AsyncClient, address: Pubkey, commitment: Commitment = None
):
    """
    异步函数：获取指定地址的账户信息并解析为JSON格式

    Args:
        client (AsyncClient): Solana RPC客户端
        address (Pubkey): 要查询的账户地址
        commitment (Commitment, optional): 事务提交选项，默认为None

    Returns:
        dict: 指定地址的账户信息（JSON格式）
    """
    return await client.get_account_info_json_parsed(address, commitment)


async def get_token_accounts_by_owner(
        client: AsyncClient,
        address: Pubkey,
        opts: TokenAccountOpts,
        commitment: Commitment = None,
):
    """
    异步函数：根据所有者地址获取令牌账户列表

    Args:
        client (AsyncClient): Solana RPC客户端
        address (Pubkey): 所有者地址
        opts (TokenAccountOpts): 令牌账户选项
        commitment (Commitment, optional): 事务提交选项，默认为None

    Returns:
        list: 令牌账户列表
    """
    return await client.get_token_accounts_by_owner(address, opts, commitment)


async def get_latest_blockhash(client: AsyncClient):
    """
    异步函数：获取最新的区块哈希

    Args:
        client (AsyncClient): Solana RPC客户端

    Returns:
        str: 最新的区块哈希
    """
    if client.blockhash_cache:
        try:
            recent_blockhash = client.blockhash_cache.get()
        except:
            recent_blockhash = (await client.get_latest_blockhash(client.commitment)).value.blockhash
    else:
        recent_blockhash = (await client.get_latest_blockhash(client.commitment)).value.blockhash
    return recent_blockhash


async def send_transaction(client: AsyncClient, transaction: VersionedTransaction):
    """
    异步函数：发送交易

    Args:
        client (AsyncClient): Solana RPC客户端
        transaction (VersionedTransaction): 要发送的交易

    Returns:
        dict: 交易结果
    """
    return await client.send_transaction(transaction)


async def confirm_transaction(
        client: AsyncClient,
        txn_signature: Signature,
        commitment: Commitment,
        sleep_seconds: float,
):
    """
    异步函数：确认交易

    Args:
        client (AsyncClient): Solana RPC客户端
        txn_signature (Signature): 交易签名
        commitment (Commitment): 事务提交选项
        sleep_seconds (float): 等待时间（秒）

    Returns:
        dict: 交易确认结果
    """
    return await client.confirm_transaction(txn_signature, commitment, sleep_seconds)


async def simulate_transaction(
        client: AsyncClient,
        transaction: VersionedTransaction,
        sig_verify: bool,
        commitment: Commitment,
):
    """
    异步函数：模拟交易

    Args:
        client (AsyncClient): Solana RPC客户端
        transaction (VersionedTransaction): 要模拟的交易
        sig_verify (bool): 是否验证签名
        commitment (Commitment): 事务提交选项

    Returns:
        dict: 模拟结果
    """
    return await client.simulate_transaction(transaction, sig_verify, commitment)


async def get_token_supply(client: AsyncClient, address: Pubkey, commitment=None):
    """
    异步函数：获取令牌供应量

    Args:
        client (AsyncClient): Solana RPC客户端
        address (Pubkey): 令牌地址
        commitment (Commitment): 事务提交选项

    Returns:
        int: 令牌供应量
    """
    return await client.get_token_supply(address, commitment)
