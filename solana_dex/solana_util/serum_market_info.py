import base58
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

import solana_dex.solana.client_wrapper as client_wrapper
from solana_dex.layout.serum_layout import MARKET_STATE_LAYOUT_V2


async def get_market_info(client: AsyncClient, market_address: any):
    """
    异步函数：获取市场信息

    Args:
        client (AsyncClient): 异步Solana RPC客户端
        market_address (any): 市场地址，可以是字符串或者Pubkey对象

    Returns:
        MARKET_STATE_LAYOUT_V2: 市场信息
    """
    if isinstance(market_address, str):
        market_pub_key = Pubkey(base58.b58decode(market_address))
    else:
        market_pub_key = Pubkey(market_address)
    market_info = await client_wrapper.get_account_info(client, market_pub_key)
    return MARKET_STATE_LAYOUT_V2.parse(market_info.value.data)


async def get_vault_signer(client: AsyncClient, vault_address: any):
    """
    异步函数：获取仓库签名者

    Args:
        client (AsyncClient): 异步Solana RPC客户端
        vault_address (any): 仓库地址，可以是字符串或者Pubkey对象

    Returns:
        Pubkey: 仓库签名者的公钥
    """
    if isinstance(vault_address, str):
        vault_pub_key = Pubkey(base58.b58decode(vault_address))
    else:
        vault_pub_key = Pubkey(vault_address)
    vault_info = await client_wrapper.get_account_info_json_parsed(client, vault_pub_key)
    vault_signer_str = vault_info.value.data.parsed["info"]["owner"]
    return Pubkey(base58.b58decode(vault_signer_str))
