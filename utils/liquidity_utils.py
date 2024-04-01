from solders.pubkey import Pubkey
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address

from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4, TOKEN_PROGRAM_ID


def get_associated_id(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'amm_associated_seed'],
        program_id
    )[0]


def get_associated_authority(program_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(bytearray([97, 109, 109, 32, 97, 117, 116, 104, 111, 114, 105, 116, 121]))],
        program_id
    )[0]


def get_associated_base_vault(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'coin_vault_associated_seed'],
        program_id
    )[0]


def get_associated_quote_vault(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'pc_vault_associated_seed'],
        program_id
    )[0]


def get_associated_lp_mint(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'lp_mint_associated_seed'],
        program_id
    )[0]


def get_associated_lp_vault(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'temp_lp_token_associated_seed'],
        program_id
    )[0]


def get_associated_target_orders(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'target_associated_seed'],
        program_id
    )[0]


def get_associated_withdraw_queue(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'withdraw_associated_seed'],
        program_id
    )[0]


def get_associated_open_orders(program_id: Pubkey, market_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [bytes(program_id), bytes(market_id), b'open_order_associated_seed'],
        program_id
    )[0]


def get_associated_config_id(program_id: Pubkey) -> Pubkey:
    return Pubkey.find_program_address(
        [b'amm_config_account_seed'],
        program_id
    )[0]


if __name__ == '__main__':
    # print(get_associated_authority(RAYDIUM_LIQUIDITY_POOL_V4))
    #
    # print("id", get_associated_id(RAYDIUM_LIQUIDITY_POOL_V4,
    #                               Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))
    # print("lp_mint", get_associated_lp_mint(RAYDIUM_LIQUIDITY_POOL_V4,
    #                                         Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))
    # print("base_vault", get_associated_base_vault(Pubkey.from_string("BiePGS754tJp9Khp7PHUcc6ahXfKPq9QBZwxvq5s8FZp"),
    #                                               Pubkey.from_string("zZzp86JcMhjdwaoxgewghCx7TC1uxq6d3fCYLm87zFE")))
    # print("quote_vault", get_associated_quote_vault(Pubkey.from_string("9ec4xZw8NhifQ5wDFRMRK9FvgcLS67ETWUbBCicCXZcw"),
    #                                                 Pubkey.from_string("zZzp86JcMhjdwaoxgewghCx7TC1uxq6d3fCYLm87zFE")))
    # print("lp_vault", get_associated_lp_vault(RAYDIUM_LIQUIDITY_POOL_V4,
    #                                           Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))
    # print("open_orders", get_associated_open_orders(RAYDIUM_LIQUIDITY_POOL_V4,
    #                                                 Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))
    # print("target_orders", get_associated_target_orders(RAYDIUM_LIQUIDITY_POOL_V4,
    #                                                     Pubkey.from_string(
    #                                                         "6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))

    # print(Pubkey.find_program_address(
    #     seeds=[bytes(Pubkey.from_string("7i6ta97y2u2Upufaig72h4jvDK8VjjhfcDy1g48jP4sU")), bytes(TOKEN_PROGRAM_ID),
    #            bytes(Pubkey.from_string("BiePGS754tJp9Khp7PHUcc6ahXfKPq9QBZwxvq5s8FZp"))],
    #     program_id=ASSOCIATED_TOKEN_PROGRAM_ID,
    # ))

    print(get_associated_token_address(Pubkey.from_string("GThUX1Atko4tqhN2NaiTazWSeFWMuiUvfFnyJyUghFMJ"),
                                       Pubkey.from_string("H3QMCaMh5LxtS9oGDwaMaRXPSPSiXVqnY4YsfrQMRjqD")))
