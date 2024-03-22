from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address

from solana_dex_v1.common.constants import LAMPORTS_PER_SOL
from solana_dex_v1.raydium.swap_util import make_swap_instruction


class SwapCore:

    async def buy(self, token_to_swap_buy, amount, payer: Keypair, pool_info):
        """
        购买函数
        :param token_to_swap_buy: 流动池id
        :param amount: 数量
        :param payer: 用户私钥
        :param pool_info: 流动池信息
        :return:
        """
        # 获取要购买代币的Pukey
        mint = Pubkey.from_string(token_to_swap_buy)
        # 计算付款金额
        amount_in = int(amount * LAMPORTS_PER_SOL)
        # create account with seed
        source = get_associated_token_address(mint, payer.pubkey())
        # swap
        dest = get_associated_token_address(payer.pubkey(), pool_info.id)
        instructions_swap = make_swap_instruction(amount_in, source, dest, payer.pubkey(), pool_info)
        print(instructions_swap)

    async def sell(self):
        pass


class TokenOwnerOffCurveError(Exception):
    pass


def get_associated_token_address_sync(
        mint: Pubkey,
        owner: Pubkey,
        allow_owner_off_curve=False,
        program_id=Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"),
        associated_token_program_id=Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
) -> Pubkey:
    if not allow_owner_off_curve and not owner.is_on_curve():
        raise TokenOwnerOffCurveError()

    address = Pubkey.find_program_address(
        [bytes(owner), bytes(program_id), bytes(mint)],
        associated_token_program_id
    )[0]

    return address


if __name__ == '__main__':
    print(get_associated_token_address(Pubkey.from_string("3JogsSZpzaYRLocVAMMUHwRSwiRh4x6pVfe42fJNG8Ms"),
                                       Pubkey.from_string("7DP9nHNDK43KbGcFKzLD5G3mYwwhVDgjenFnXM8JcDxn")))

    print(get_associated_token_address(Pubkey.from_string("7DP9nHNDK43KbGcFKzLD5G3mYwwhVDgjenFnXM8JcDxn"),
                                       Pubkey.from_string("3JogsSZpzaYRLocVAMMUHwRSwiRh4x6pVfe42fJNG8Ms")))

    print(get_associated_token_address_sync(Pubkey.from_string("3JogsSZpzaYRLocVAMMUHwRSwiRh4x6pVfe42fJNG8Ms"),
                                            Pubkey.from_string("7DP9nHNDK43KbGcFKzLD5G3mYwwhVDgjenFnXM8JcDxn")))
