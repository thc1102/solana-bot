import asyncio

import base58
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

from solana_dex.common.direction import Direction
from solana_dex.common.constants import RAYDIUM_AMM_AUTHORITY, SOL_MINT_ADDRESS
from solana_dex.common.unit import Unit
from solana_dex.solana_util.raydium_pool_info import (
    get_lp_token_address,
    get_mint_address,
    get_pool_info,
    get_pool_vaults_balance,
    get_pool_vaults_decimals,
    get_token_program_id,
)
from solana_dex.solana_util.serum_market_info import get_market_info, get_vault_signer


class RaydiumPool:
    def __init__(self, client: AsyncClient, pool_address: str):
        self.client = client
        self.subscription = None
        self.price_changes_callbacks = []
        self.pool_address = pool_address
        self.initialization_task = asyncio.create_task(self.initialize())


    async def initialize(self):
        # 获取池信息和市场信息
        self.pool_info = await get_pool_info(self.client, self.pool_address)
        self.market_info = await get_market_info(self.client, self.pool_info.market_id)
        # AMM ID
        self.amm_id = Pubkey(base58.b58decode(self.pool_address))
        # AMM 权限
        self.amm_authority = RAYDIUM_AMM_AUTHORITY
        # AMM 开放订单
        self.amm_open_orders = Pubkey(self.pool_info.open_orders)
        # AMM 目标订单
        self.amm_target_orders = Pubkey(self.pool_info.target_orders)
        # 池中代币账户
        self.pool_coin_token_account = Pubkey(self.pool_info.base_vault)
        self.pool_pc_token_account = Pubkey(self.pool_info.quote_vault)
        # 市场程序 ID
        self.market_program_id = Pubkey(self.pool_info.market_program_id)
        # Serum 市场信息
        self.serum_market = Pubkey(self.pool_info.market_id)
        self.serum_bids = Pubkey(self.market_info.bids)
        self.serum_asks = Pubkey(self.market_info.asks)
        self.serum_event_queue = Pubkey(self.market_info.event_queue)
        self.serum_coin_vault_account = Pubkey(self.market_info.base_vault)
        self.serum_pc_vault_account = Pubkey(self.market_info.quote_vault)
        self.serum_vault_signer = await get_vault_signer(self.client, self.market_info.base_vault)
        # 基础代币地址和报价代币地址s
        self.base_mint_address = await get_mint_address(self.client, self.pool_info.base_vault)
        self.quote_mint_address: Pubkey = await get_mint_address(
            self.client, self.pool_info.quote_vault
        )
        # 基础代币和报价代币的小数位数
        self.base_decimals, self.quote_decimals = await get_pool_vaults_decimals(
            self.client, self.pool_coin_token_account, self.pool_pc_token_account
        )
        # 代币程序 ID
        self.token_program_id = await get_token_program_id(self.client, self.base_mint_address)

        # LP 代币地址
        self.lp_token_address = await get_lp_token_address(self.pool_info.market_id)

        # 如果基础代币是 SOL，则交换基础代币和报价代币的相关信息
        if self.base_mint_address == SOL_MINT_ADDRESS:
            self.base_mint_address, self.quote_mint_address = (
                self.quote_mint_address,
                self.base_mint_address,
            )
            self.base_decimals, self.quote_decimals = (
                self.quote_decimals,
                self.base_decimals,
            )
            self.token_program_id = await get_token_program_id(self.client, self.base_mint_address)
            self.pool_info.base_vault, self.pool_info.quote_vault = (
                self.pool_info.quote_vault,
                self.pool_info.base_vault,
            )
        # 如果报价代币是 SOL，则抛出异常
        if self.quote_mint_address == SOL_MINT_ADDRESS:
            self.quote_token = "SOL"
        else:
            raise Exception("不支持的报价代币")

        # 更新池代币余额
        await self.update_pool_vaults_balance()

    def to_dict(self):
        return {
            "pool_address": self.pool_address,
            "pool_info": self.pool_info,
            "market_info": self.market_info,
            "amm_id": self.amm_id,
            "amm_authority": self.amm_authority,
            "amm_open_orders": self.amm_open_orders,
            "amm_target_orders": self.amm_target_orders,
            "pool_coin_token_account": self.pool_coin_token_account,
            "pool_pc_token_account": self.pool_pc_token_account,
            "market_program_id": self.market_program_id,
            "serum_market": self.serum_market,
            "serum_bids": self.serum_bids,
            "serum_asks": self.serum_asks,
            "serum_event_queue": self.serum_event_queue,
            "serum_coin_vault_account": self.serum_coin_vault_account,
            "serum_pc_vault_account": self.serum_pc_vault_account,
            "serum_vault_signer": self.serum_vault_signer,
            "base_mint_address": self.base_mint_address,
            "quote_mint_address": self.quote_mint_address,
            "base_decimals": self.base_decimals,
            "quote_decimals": self.quote_decimals,
            "token_program_id": self.token_program_id,
            "lp_token_address": self.lp_token_address,
        }

    def get_mint_address(self):
        return self.base_mint_address

    async def update_pool_vaults_balance(self, commitment: str = "confirmed"):
        self.base_vault_balance, self.quote_vault_balance = await get_pool_vaults_balance(
            self.client,
            Pubkey(self.pool_info.base_vault),
            Pubkey(self.pool_info.quote_vault),
            commitment,
        )

    def get_price(
            self,
            in_amount: float,
            direction: Direction,
            return_price_unit: Unit = Unit.QUOTE_TOKEN,
            update_vault_balance=False,
            commitment="confirmed",
    ):
        """
        返回：
            [0]: 基于 in_amount 估算的价格（您可以通过 return_price_unit 更改单位）
            [1]: 基于池余额的估算价格
            [2]: 预期的输出量。您可以将此量用于最小输出量以及滑点允许
            [3]: 减去交换费和网络费后的预期输入量
        """
        if update_vault_balance:
            self.update_pool_vaults_balance(commitment)
        base_vault_balance = self.base_vault_balance
        quote_vault_balance = self.quote_vault_balance

        # 交换费：0.25%
        swap_fee = 0.25
        # 网络费：暂不考虑网络费，因为实际上很小（@TODO: 修复我）
        network_fee = 0.00

        # k = x * y
        pool_k = base_vault_balance * quote_vault_balance

        if direction == Direction.SPEND_QUOTE_TOKEN:
            # 对于报价池，+ in_amount
            delta_quote_vault = in_amount
            # 交换费将从报价金额中扣除
            delta_quote_vault -= in_amount * (swap_fee / 100)
            # 网络费
            delta_quote_vault -= network_fee
            # 计算 delta base_vault
            delta_base_vault = base_vault_balance - pool_k / (
                    quote_vault_balance + delta_quote_vault
            )
        elif direction == Direction.SPEND_BASE_TOKEN:
            # 对于基础池，+ in_amount
            delta_base_vault = in_amount
            # 交换费将从基础金额中扣除
            delta_base_vault -= in_amount * (swap_fee / 100)
            # 网络费
            delta_base_vault -= network_fee
            # 计算 delta quote_vault
            delta_quote_vault = quote_vault_balance - pool_k / (
                    base_vault_balance + delta_base_vault
            )
        else:
            raise Exception("不支持的方向")

        base_price = base_vault_balance / quote_vault_balance
        price = delta_base_vault / delta_quote_vault

        if return_price_unit == Unit.BASE_TOKEN:
            return_price = price
            return_base_price = base_price
        elif return_price_unit == Unit.QUOTE_TOKEN:
            return_price = 1 / price
            return_base_price = 1 / base_price
        else:
            raise Exception("不支持的返回价格单位")

        if direction == Direction.SPEND_QUOTE_TOKEN:
            return return_price, return_base_price, delta_base_vault, delta_quote_vault
        elif direction == Direction.SPEND_BASE_TOKEN:
            return return_price, return_base_price, delta_quote_vault, delta_base_vault
        else:
            raise Exception("不支持的方向")

    def convert_base_token_amount_to_tx_format(self, amount: float):
        """
        将基础代币金额转换为交易格式的整数形式。

        参数：
            amount (float): 基础代币金额

        返回：
            int: 转换后的交易格式的整数金额
        """
        return int(amount * 10 ** self.base_decimals)

    def convert_quote_token_amount_to_tx_format(self, amount: float):
        """
        将报价代币金额转换为交易格式的整数形式。

        参数：
            amount (float): 报价代币金额

        返回：
            int: 转换后的交易格式的整数金额
        """
        return int(amount * 10 ** self.quote_decimals)

    def convert_base_token_amount_from_tx_format(self, amount: int):
        """
        将基础代币交易格式的整数金额转换为正常金额形式。

        参数：
            amount (int): 基础代币交易格式的整数金额

        返回：
            float: 转换后的基础代币金额
        """
        return amount / 10 ** self.base_decimals

    def convert_quote_token_amount_from_tx_format(self, amount: int):
        """
        将报价代币交易格式的整数金额转换为正常金额形式。

        参数：
            amount (int): 报价代币交易格式的整数金额

        返回：
            float: 转换后的报价代币金额
        """
        return amount / 10 ** self.quote_decimals
