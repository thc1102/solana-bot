import solders.system_program as sp
import spl.token.instructions as spl_token
from solana.rpc.async_api import AsyncClient
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address
from solders.transaction import VersionedTransaction
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
        AccountMeta(pubkey=Pubkey.from_string(pool_info.id), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.authority), is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.openOrders), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.targetOrders), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.baseVault), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.quoteVault), is_signer=False, is_writable=True),
        AccountMeta(pubkey=OPENBOOK_MARKET, is_signer=False, is_writable=False),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.marketId), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.marketBids), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.marketAsks), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.marketEventQueue), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.marketBaseVault), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.marketQuoteVault), is_signer=False, is_writable=True),
        AccountMeta(pubkey=Pubkey.from_string(pool_info.marketAuthority), is_signer=False, is_writable=False),
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
            pool: PoolInfo,
            payer: Keypair,
            unit_price: int = 25000,
            unit_budget: int = 600000,
    ):
        self.client = client
        self.pool = pool
        self.payer = payer
        # token address
        self.baseMint = Pubkey.from_string(pool.baseMint)
        self.TOKEN_PROGRAM_ID = TOKEN_PROGRAM_ID
        # quote address (supposed to be SOL)
        self.quoteMint = Pubkey.from_string(pool.quoteMint)
        # budget
        self.unit_price = unit_price
        self.unit_budget = unit_budget
        # initialize instructions
        self.instructions = []
        self.new_keypair = None

    async def compile_versioned_transaction(self):
        try:
            recent_blockhash = self.client.blockhash_cache.get()
        except:
            recent_blockhash = (await self.client.get_latest_blockhash()).value.blockhash
        compiled_message = MessageV0.try_compile(
            self.payer.pubkey(),
            self.instructions,
            [],  # lookup tables
            recent_blockhash,
        )
        keypairs = [self.payer]
        if self.new_keypair is not None:
            keypairs.append(self.new_keypair)
        return VersionedTransaction(compiled_message, keypairs)

    def append_swap(
            self, amount_in: int, source: Pubkey, dest: Pubkey
    ):
        self.instructions.append(
            make_swap_instruction(
                amount_in,
                source,
                dest,
                self.payer.pubkey(),
                self.pool,
            )
        )

    async def wsol_append_buy(self, amount_in: int, check_associated_token_account_exists=True):
        # 前提必须存在wsol代币地址
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        source = get_associated_token_address(self.payer.pubkey(), SOL_MINT_ADDRESS)
        dest = get_associated_token_address(self.payer.pubkey(), self.baseMint)
        if check_associated_token_account_exists:
            await self.append_if_not_exists_create_associated_token_account(self.baseMint)
        self.append_swap(amount_in, source, dest)

    async def sol_append_buy(self, amount_in: int, check_associated_token_account_exists=True, ):
        pay_for_rent = await AsyncToken.get_min_balance_rent_for_exempt_for_account(self.client)
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        source = self.append_create_account(pay_for_rent, amount_in)
        self.append_initialize_account(source.pubkey())
        if check_associated_token_account_exists:
            await self.append_if_not_exists_create_associated_token_account(self.baseMint)
        dest = get_associated_token_address(self.payer.pubkey(), self.baseMint)
        self.append_swap(amount_in, source.pubkey(), dest)
        self.append_close_account(source.pubkey())

    async def wsol_append_sell(self, amount_in: int):
        # 前提必须存在wsol代币地址
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        source = get_associated_token_address(self.payer.pubkey(), self.baseMint)
        dest = get_associated_token_address(self.payer.pubkey(), SOL_MINT_ADDRESS)
        self.append_swap(amount_in, source, dest)

    async def sol_append_sell(self, amount_in: int):
        pay_for_rent = await AsyncToken.get_min_balance_rent_for_exempt_for_account(self.client)
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        source = get_associated_token_address(self.payer.pubkey(), self.baseMint)
        dest = self.append_create_account(pay_for_rent, 0)
        self.append_initialize_account(dest.pubkey())
        self.append_swap(amount_in, source, dest.pubkey())
        self.append_close_account(dest.pubkey())

    def append_set_compute_budget(self, unit_price: int, unit_limit: int):
        self.instructions.append(set_compute_unit_price(unit_price))
        self.instructions.append(set_compute_unit_limit(unit_limit))

    def append_close_account(self, account: Pubkey):
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

    def append_create_associated_token_account(self, mint: Pubkey):
        self.instructions.append(
            create_associated_token_account(
                self.payer.pubkey(), self.payer.pubkey(), mint
            )
        )

    def append_create_account(self, lamports: int, amount: int == 0):
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
        if amount != 0:
            self.instructions.append(
                sp.transfer(
                    sp.TransferParams(
                        from_pubkey=self.payer.pubkey(),
                        to_pubkey=new_keypair.pubkey(),
                        lamports=amount,
                    )
                )
            )
        self.new_keypair = new_keypair
        return new_keypair

    def append_initialize_account(self, source: Pubkey):
        # initialize account
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

    async def append_if_not_exists_create_associated_token_account(self, mint: Pubkey):
        # arr = (await self.client.get_token_accounts_by_owner(self.payer.pubkey(), TokenAccountOpts(mint))).value
        #
        # if len(arr) > 0:
        #     return

        self.instructions.append(
            create_associated_token_account(
                self.payer.pubkey(), self.payer.pubkey(), mint
            )
        )


class AccountTransactionBuilder:
    def __init__(self, client: AsyncClient, payer: Keypair):
        self.client = client
        self.payer = payer
        self.TOKEN_PROGRAM_ID = TOKEN_PROGRAM_ID
        self.instructions = []

    def append_close_account(self, account: Pubkey):
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

    async def compile_versioned_transaction(self):
        try:
            recent_blockhash = self.client.blockhash_cache.get()
        except:
            recent_blockhash = (await self.client.get_latest_blockhash()).value
        compiled_message = MessageV0.try_compile(
            self.payer.pubkey(),
            self.instructions,
            [],  # lookup tables
            recent_blockhash.blockhash,
        )
        keypairs = [self.payer]
        return VersionedTransaction(compiled_message, keypairs)
