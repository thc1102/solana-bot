import base58
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

import solana_dex.solana.client_wrapper as client_wrapper
from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4
from solana_dex.layout.raydium_layout import LIQUIDITY_STATE_LAYOUT_V4


async def get_pool_info(client: AsyncClient, pool_address: str):
    """
    异步函数：获取池子信息

    Args:
        client (AsyncClient): Solana RPC客户端
        pool_address (str): 池子地址

    Returns:
        LIQUIDITY_STATE_LAYOUT_V4: 池子信息
    """
    target_token_pool_pub_key = Pubkey(base58.b58decode(pool_address))
    pool_info = await client_wrapper.get_account_info(client, target_token_pool_pub_key)
    return LIQUIDITY_STATE_LAYOUT_V4.parse(pool_info.value.data)


async def get_pool_vaults(client: AsyncClient, pool_address: str):
    """
    异步函数：获取池子仓库

    Args:
        client (AsyncClient): Solana RPC客户端
        pool_address (str): 池子地址

    Returns:
        tuple: (基础代币仓库地址, 引用代币仓库地址)
    """
    pool_info = await get_pool_info(client, pool_address)
    base_vault = pool_info.base_vault
    quote_vault = pool_info.quote_vault
    return Pubkey(base_vault), Pubkey(quote_vault)


async def get_lp_token_address(pool_info_market_id: str):
    """
    异步函数：获取LP代币地址

    Args:
        pool_info_market_id (str): 池子信息的市场ID

    Returns:
        Pubkey: LP代币地址
    """
    buffer_text = b"lp_mint_associated_seed"
    program_addr, _ = Pubkey.find_program_address(
        [
            bytes(RAYDIUM_LIQUIDITY_POOL_V4),
            bytes(pool_info_market_id),
            buffer_text,
        ],
        RAYDIUM_LIQUIDITY_POOL_V4,
    )
    return program_addr


async def get_pool_vaults_balance(
        client: AsyncClient, base_vault: Pubkey, quote_vault: Pubkey, commitment="confirmed"
):
    """
    异步函数：获取池子仓库余额

    Args:
        client (AsyncClient): Solana RPC客户端
        base_vault (Pubkey): 基础代币仓库地址
        quote_vault (Pubkey): 引用代币仓库地址
        commitment (str, optional): 事务提交选项，默认为"confirmed"

    Returns:
        tuple: (基础代币仓库余额, 引用代币仓库余额)
    """
    base_vault_token_account_balance = await client_wrapper.get_token_account_balance(
        client, base_vault, commitment=commitment
    )
    quote_vault_token_account_balance = await client_wrapper.get_token_account_balance(
        client, quote_vault, commitment=commitment
    )
    return (
        int(base_vault_token_account_balance.value.amount) / 10 ** int(base_vault_token_account_balance.value.decimals),
        int(quote_vault_token_account_balance.value.amount) / 10 ** int(
            quote_vault_token_account_balance.value.decimals),
    )


async def get_pool_vaults_decimals(client: AsyncClient, base_vault: Pubkey, quote_vault: Pubkey):
    """
    异步函数：获取池子仓库小数位数

    Args:
        client (AsyncClient): Solana RPC客户端
        base_vault (Pubkey): 基础代币仓库地址
        quote_vault (Pubkey): 引用代币仓库地址

    Returns:
        tuple: (基础代币仓库小数位数, 引用代币仓库小数位数)
    """
    base_vault_token_account_balance = await client_wrapper.get_token_account_balance(
        client, base_vault
    )
    quote_vault_token_account_balance = await client_wrapper.get_token_account_balance(
        client, quote_vault
    )
    return (
        int(base_vault_token_account_balance.value.decimals),
        int(quote_vault_token_account_balance.value.decimals),
    )


async def get_mint_address(client: AsyncClient, token_account: any):
    """
    异步函数：获取代币的Mint地址

    Args:
        client (AsyncClient): Solana RPC客户端
        token_account (any): 代币账户信息

    Returns:
        Pubkey: 代币的Mint地址
    """
    if isinstance(token_account, str):
        token_account_pub_key = Pubkey(base58.b58decode(token_account))
    else:
        token_account_pub_key = Pubkey(token_account)
    token_account_info = await client_wrapper.get_account_info_json_parsed(
        client, token_account_pub_key
    )
    addr_str = token_account_info.value.data.parsed["info"]["mint"]
    return Pubkey(base58.b58decode(addr_str))


async def get_token_program_id(client: AsyncClient, mint_address: Pubkey):
    """
    异步函数：获取代币的程序ID

    Args:
        client (AsyncClient): Solana RPC客户端
        mint_address (Pubkey): 代币的Mint地址

    Returns:
        Pubkey: 代币的程序ID
    """
    token_account_info = await client_wrapper.get_account_info_json_parsed(
        client, mint_address
    )
    return token_account_info.value.owner
