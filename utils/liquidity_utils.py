from solders.pubkey import Pubkey


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
