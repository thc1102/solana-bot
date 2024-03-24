import solders.system_program as sp
import spl.token.instructions as spl_token
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from solders.compute_budget import set_compute_unit_price, set_compute_unit_limit
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address
from solders.transaction import VersionedTransaction
from spl.token.async_client import AsyncToken
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import close_account, CloseAccountParams, create_associated_token_account

from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4, OPENBOOK_MARKET, SOL_MINT_ADDRESS
from solana_dex.layout.raydium_layout import ROUTE_DATA_LAYOUT
from solana_dex.raydium.models import ApiPoolInfo


def make_swap_instruction(
        amount_in: int,
        token_account_in: Pubkey,
        token_account_out: Pubkey,
        owner: Pubkey,
        pool_info: ApiPoolInfo
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
            pool: ApiPoolInfo,
            payer: Keypair,
            unit_price: int = 25000,
            unit_budget: int = 600000,
    ):
        self.client = client
        self.pool = pool
        self.payer = payer
        # token address
        self.baseMint = pool.baseMint
        self.TOKEN_PROGRAM_ID = TOKEN_PROGRAM_ID
        # quote address (supposed to be SOL)
        self.quoteMint = pool.quoteMint
        # budget
        self.unit_price = unit_price
        self.unit_budget = unit_budget
        # initialize instructions
        self.instructions = []

    async def compile_versioned_transaction(self):
        recent_blockhash = (await self.client.get_latest_blockhash()).value
        compiled_message = MessageV0.try_compile(
            self.payer.pubkey(),
            self.instructions,
            [],  # lookup tables
            recent_blockhash.blockhash,
        )
        return VersionedTransaction(compiled_message, [self.payer])

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

    async def append_sell(self, amount_in: int, check_associated_token_account_exists=True):
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        source = get_associated_token_address(self.payer.pubkey(), self.baseMint)
        dest = get_associated_token_address(self.payer.pubkey(), self.quoteMint)
        if check_associated_token_account_exists:
            await self.append_if_not_exists_create_associated_token_account(self.quoteMint)
        self.append_swap(amount_in, source, dest)
        self.append_close_account(dest)
        print(self.instructions)

    async def append_buy(
            self,
            amount_in: int,
            check_associated_token_account_exists=True,
    ):
        pay_for_rent = await AsyncToken.get_min_balance_rent_for_exempt_for_account(self.client)
        lamports = pay_for_rent + amount_in
        self.append_set_compute_budget(self.unit_price, self.unit_budget)
        source = self.append_create_account_with_seed(lamports)
        self.append_initialize_account(source)
        if check_associated_token_account_exists:
            await self.append_if_not_exists_create_associated_token_account(self.baseMint)
        dest = get_associated_token_address(self.payer.pubkey(), self.baseMint)
        self.append_swap(amount_in, source, dest)
        self.append_close_account(source)

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

    def append_create_account_with_seed(self, lamports: int):
        # create account with seed
        seed = str(Keypair().pubkey())[0:32]  # use this as the seed for the new account
        source = Pubkey.create_with_seed(
            self.payer.pubkey(), seed, self.TOKEN_PROGRAM_ID
        )
        self.instructions.append(
            sp.create_account_with_seed(
                sp.CreateAccountWithSeedParams(
                    from_pubkey=self.payer.pubkey(),
                    to_pubkey=source,
                    base=self.payer.pubkey(),
                    seed=seed,
                    lamports=lamports,
                    space=165,
                    owner=self.TOKEN_PROGRAM_ID,
                )
            )
        )
        return source

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
        arr = (await self.client.get_token_accounts_by_owner(self.payer.pubkey(), TokenAccountOpts(mint))).value

        if len(arr) > 0:
            return

        self.instructions.append(
            create_associated_token_account(
                self.payer.pubkey(), self.payer.pubkey(), mint
            )
        )
