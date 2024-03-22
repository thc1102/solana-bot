from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address

from solana_dex_v1.common.constants import LAMPORTS_PER_SOL
from solana_dex_v1.raydium.swap_util import make_swap_instruction


class SwapCore:

    async def buy(self, token_to_swap_buy, amount, payer: Keypair, pool_info):
        # 获取要购买代币的Pukey
        mint = Pubkey.from_string(token_to_swap_buy)
        # 计算付款金额
        amount_in = int(amount * LAMPORTS_PER_SOL)
        # create account with seed
        # source = await self.append_create_account_with_seed(lamports)
        # swap
        # dest = get_associated_token_address(payer.pubkey(), mint)
        # instructions_swap = make_swap_instruction(amount_in, source, dest, payer, pool_info)

    async def sell(self):
        pass
