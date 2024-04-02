from solders.pubkey import Pubkey
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address

from solana_dex.common.constants import RAYDIUM_LIQUIDITY_POOL_V4, TOKEN_PROGRAM_ID, SOL_MINT_ADDRESS, OPENBOOK_MARKET, \
    RAY_AUTHORITY_V4


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
    # print("lp_vault", get_associated_lp_vault(RAYDIUM_LIQUIDITY_POOL_V4,
    #                                           Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))
    # print("open_orders", get_associated_open_orders(RAYDIUM_LIQUIDITY_POOL_V4,
    #                                                 Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))
    # print("target_orders", get_associated_target_orders(RAYDIUM_LIQUIDITY_POOL_V4,
    #                                                     Pubkey.from_string(
    #                                                         "6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))

    print("base_vault", get_associated_base_vault(RAYDIUM_LIQUIDITY_POOL_V4,
                                                  Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))

    print("quote_vault", get_associated_quote_vault(RAYDIUM_LIQUIDITY_POOL_V4,
                                                    Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))

    print("========================")

    print("base_vault", get_associated_base_vault(RAY_AUTHORITY_V4,
                                                  Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))
    print("quote_vault", get_associated_quote_vault(RAY_AUTHORITY_V4,
                                                    Pubkey.from_string("6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG")))

    # {"id":"zZzp86JcMhjdwaoxgewghCx7TC1uxq6d3fCYLm87zFE",
    # "baseMint":"BiePGS754tJp9Khp7PHUcc6ahXfKPq9QBZwxvq5s8FZp",
    # "quoteMint":"So11111111111111111111111111111111111111112",
    # "lpMint":"5iZsGVkSGwtiqWzyV4RprdJGkjVgJZ6JZ2SLHwu1Y8TH",
    # "baseDecimals":9,"quoteDecimals":9,"lpDecimals":9,"version":4,
    # "programId":"675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8",
    # "authority":"5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
    # "openOrders":"8UHqksqCfwU8quUp463sshzPPB8idzHdnX4Mw5fsvAoR",
    # "targetOrders":"Qw6rBxPob153Qi6n6BD2rHwBmvDjP17Uo5LkCjfYmFX",
    # "baseVault":"CvRawNjcEmwkvntCtpUwruwKrWspG2R1B3DuSa2qCauQ",
    # "quoteVault":"9ec4xZw8NhifQ5wDFRMRK9FvgcLS67ETWUbBCicCXZcw",
    # "withdrawQueue":"11111111111111111111111111111111",
    # "lpVault":"11111111111111111111111111111111",
    # "marketVersion":4,
    # "marketProgramId":"srmqPvymJeFKQ4zGQed1GFppgkRHL9kaELCbyksJtPX",
    # "marketId":"6LCnUWTjPN55FwVtMWhiDHo4AXa7Abg8suDrJiTrHEGG",
    # "marketAuthority":"93M2YE4QHChbEb68BKB6HWdYpZZJz3Wqsir8bEBHywKp",
    # "marketBaseVault":"GPyKT2F6GUKGa62GMmPrhFAEfE1cxTVAaxNChM9PvUh",
    # "marketQuoteVault":"GsznDfAYbbRoP4ep6FiHrsUby87G3XmZQGt3yq5t6zc2",
    # "marketBids":"GWje1eXmo1QnCxEDgokY9FHr6v76aX7SmwWeptyLVrFa",
    # "marketAsks":"Cyj1gw28BaPx8xiRPTHXeSsQaraptSexaZGoVe8V3Rrx",
    # "marketEventQueue":"EaYoQyDnhLup8SMQrzBbjeLNBfA17NaQVFzkpvZqPE91",
    # "lookupTableAccount":"A8MGRr6n2EKUweTjb2ffL5bunwfZPR8L5yYpsComWJkj"}