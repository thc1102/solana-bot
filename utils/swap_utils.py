import time

import solders.system_program as sp
import spl.token.instructions as spl_token
from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Finalized, Processed, Confirmed
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address
from spl.token._layouts import ACCOUNT_LAYOUT
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import close_account, CloseAccountParams, create_associated_token_account

from solana_dex.common.constants import OPENBOOK_MARKET, RAYDIUM_LIQUIDITY_POOL_V4, SOL_MINT_ADDRESS
from solana_dex.layout.raydium import ROUTE_DATA_LAYOUT
from solana_dex.model.pool import PoolInfo


def make_swap_instruction(
        amount_in: int,
        token_account_in: Pubkey,
        token_account_out: Pubkey,
        owner: Pubkey,
        pool_info: PoolInfo
) -> Instruction:
    keys = [
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.id, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.authority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.openOrders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.targetOrders, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.baseVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.quoteVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=OPENBOOK_MARKET, is_signer=False, is_writable=False),
        AccountMeta(pubkey=pool_info.marketId, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketBids, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketAsks, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketEventQueue, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketBaseVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketQuoteVault, is_signer=False, is_writable=True),
        AccountMeta(pubkey=pool_info.marketAuthority, is_signer=False, is_writable=False),
        AccountMeta(pubkey=token_account_in, is_signer=False, is_writable=True),
        AccountMeta(pubkey=token_account_out, is_signer=False, is_writable=True),
        AccountMeta(pubkey=owner, is_signer=True, is_writable=False)
    ]

    data = ROUTE_DATA_LAYOUT.build(
        dict(
            instruction=9,
            amountIn=int(amount_in),
            minAmountOut=0
        )
    )
    return Instruction(RAYDIUM_LIQUIDITY_POOL_V4, data, keys)


class SwapTransactionBuilder:
    def __init__(
            self,
            client: AsyncClient,
            payer: Keypair,
            unit_price: int = 25000,
            unit_budget: int = 600000,
    ):
        self.payer = payer
        self.client = client
        self.unit_price = unit_price
        self.unit_budget = unit_budget
        self.TOKEN_PROGRAM_ID = TOKEN_PROGRAM_ID
        self.instructions = []
        self.new_keypair_list = []

    async def compile_signed_transaction(self):
        t = time.time()
        response = await self.client.get_latest_blockhash(Confirmed)
        logger.info(f"{response.context.slot}, {response.value.blockhash}, {time.time() - t}")
        recent_blockhash = response.value.blockhash
        keypairs = [self.payer]
        if len(self.new_keypair_list) != 0:
            keypairs.extend(self.new_keypair_list)
        tx = Transaction(recent_blockhash, fee_payer=self.payer.pubkey(), instructions=self.instructions)
        tx.sign(*keypairs)
        return tx

    def append_set_compute_budget(self, unit_price: int, unit_budget: int):
        # 添加 优先费
        self.instructions.append(set_compute_unit_price(unit_price))
        self.instructions.append(set_compute_unit_limit(unit_budget))

    def append_swap(self, amount_in: int, source: Pubkey, dest: Pubkey, pool_info: PoolInfo):
        # 添加 swap
        self.instructions.append(
            make_swap_instruction(
                amount_in,
                source,
                dest,
                self.payer.pubkey(),
                pool_info
            )
        )

    def append_associated_token_account(self, mint: Pubkey):
        # 添加 代币账户
        self.instructions.append(
            create_associated_token_account(
                self.payer.pubkey(), self.payer.pubkey(), mint
            )
        )

    async def check_associated_token_account(self, mint: Pubkey):
        # 检查代币账户是否存在存在
        arr = (await self.client.get_token_accounts_by_owner(self.payer.pubkey(), TokenAccountOpts(mint))).value
        if len(arr) > 0:
            return True
        else:
            return False

    def append_close_account(self, account: Pubkey):
        # 添加 关闭账户
        self.instructions.append(
            close_account(
                CloseAccountParams(
                    account=account,
                    dest=self.payer.pubkey(),
                    owner=self.payer.pubkey(),
                    program_id=self.TOKEN_PROGRAM_ID,
                )
            )
        )

    def append_initialize_account(self, source: Pubkey):
        # 添加初始化账户
        self.instructions.append(
            spl_token.initialize_account(
                spl_token.InitializeAccountParams(
                    account=source,
                    mint=SOL_MINT_ADDRESS,
                    owner=self.payer.pubkey(),
                    program_id=self.TOKEN_PROGRAM_ID,
                )
            )
        )

    def append_transfer(self, new_pubkey: Pubkey, amount: int):
        # 添加 转账
        self.instructions.append(
            sp.transfer(
                sp.TransferParams(
                    from_pubkey=self.payer.pubkey(),
                    to_pubkey=new_pubkey,
                    lamports=amount,
                )
            )
        )

    def append_create_account(self, lamports: int):
        # 添加 创建账户 并返回账户密钥
        new_keypair = Keypair()
        self.instructions.append(
            sp.create_account(
                sp.CreateAccountParams(
                    from_pubkey=self.payer.pubkey(),
                    to_pubkey=new_keypair.pubkey(),
                    lamports=lamports,
                    space=ACCOUNT_LAYOUT.sizeof(),
                    owner=self.TOKEN_PROGRAM_ID,
                )
            )
        )
        self.new_keypair_list.append(new_keypair)
        return new_keypair

    async def append_transaction(
            self,
            pool_info: PoolInfo,
            amount_in: int,
            is_buy: bool,
            is_sol: bool,
            is_create_associated_token: bool = True
    ):
        """
        添加交易指令。

        Args:
            pool_info (PoolInfo): 交易所需的池信息。
            amount_in (int): 输入的数量。
            is_buy (bool): 是否为买入操作，True 表示买入，False 表示卖出。
            is_sol (bool): 是否为 SOL 交易，True 表示 SOL 交易，False 表示代币交易。
            is_create_associated_token (bool, optional): 是否创建相关联的代币账户。默认为 True。

        Returns:
            Optional[Keypair]: 如果是 SOL 交易，则返回创建的账户的 Keypair；否则返回 None。
        """
        base_mint = pool_info.baseMint
        pay_for_rent = await AsyncToken.get_min_balance_rent_for_exempt_for_account(self.client) if is_sol else None
        self.append_set_compute_budget(self.unit_price, self.unit_budget)

        # 确定源和目标的 mint
        source_mint = SOL_MINT_ADDRESS if is_buy else base_mint
        dest_mint = base_mint if is_buy else SOL_MINT_ADDRESS

        # 创建相关联的代币账户
        if is_create_associated_token:
            self.append_associated_token_account(base_mint)

        # 初始化源地址
        if is_sol:
            source_keypair = self.append_create_account(pay_for_rent)
            source = source_keypair.pubkey()
            self.append_transfer(source, amount_in)
            self.append_initialize_account(source)
        else:
            source = get_associated_token_address(self.payer.pubkey(), source_mint)

        # 初始化目标地址
        dest = get_associated_token_address(self.payer.pubkey(), dest_mint)

        self.append_swap(amount_in, source, dest, pool_info)

        # 关闭 SOL 交易的源地址
        if is_sol:
            self.append_close_account(source)
