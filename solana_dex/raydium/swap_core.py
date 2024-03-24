from loguru import logger
from solana.rpc.commitment import Confirmed, Commitment
from solana.transaction import Transaction
from solders.compute_budget import set_compute_unit_price
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.system_program import create_account_with_seed, CreateAccountWithSeedParams
from solders.token.associated import get_associated_token_address
from solders.transaction import VersionedTransaction
from spl.token.async_client import AsyncToken
from spl.token.core import _TokenCore
from spl.token.instructions import create_associated_token_account, CloseAccountParams, close_account

from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.common.constants import LAMPORTS_PER_SOL, SOL_MINT_ADDRESS, TOKEN_PROGRAM_ID
from solana_dex.raydium.models import ApiPoolInfo
from solana_dex.raydium.swap_util import make_swap_instruction, SwapTransactionBuilder
from solana_dex.solana.solana_client import SolanaRPCClient
from solana_dex.solana.wallet import Wallet


class SwapCore:
    def __init__(self, wallet: Wallet, pool_info: ApiPoolInfo, compute_unit_price: int = 250000):
        self.wallet = wallet
        self.pool_info = pool_info
        self.compute_unit_price = compute_unit_price

    async def _buy(self, token_mint: Pubkey, amount_in: int):
        """
        购买函数
        :param token_mint: 获取的代币mint
        :param amount_in: 支付数量
        :return:
        """
        swap_transaction_builder = SwapTransactionBuilder(GlobalVariables.SolaraClient, self.pool_info,
                                                          self.wallet.keypair, unit_price=self.compute_unit_price)

        await swap_transaction_builder.append_buy(amount_in,
                                                  not self.wallet.check_token_accounts(token_mint))
        transaction = await swap_transaction_builder.compile_versioned_transaction()
        txn_signature = (await GlobalVariables.SolaraClient.send_transaction(transaction)).value
        logger.info(f"交易创建完成 {txn_signature}")
        resp = await GlobalVariables.SolaraClient.confirm_transaction(
            txn_signature,
            Confirmed,
        )
        return txn_signature

    async def _sell(self, amount_in: int):
        """
        购买函数
        :param amount_in: 支付数量
        :return:
        """
        swap_transaction_builder = SwapTransactionBuilder(GlobalVariables.SolaraClient, self.pool_info,
                                                          self.wallet.keypair, unit_price=self.compute_unit_price)

        await swap_transaction_builder.append_sell(amount_in, not self.wallet.check_token_accounts(SOL_MINT_ADDRESS))
        transaction = await swap_transaction_builder.compile_versioned_transaction()
        txn_signature = (await GlobalVariables.SolaraClient.send_transaction(transaction)).value
        logger.info(f"交易创建完成 {txn_signature}")
        resp = await SolanaRPCClient.confirm_transaction(
            txn_signature,
            Confirmed,
        )
        return txn_signature

    async def buy(self, mint: Pubkey, amount: float):
        amount_in = int(amount * LAMPORTS_PER_SOL)
        try:
            txn_signature = await self._buy(mint, amount_in)
            logger.info(f"购买结束 https://solscan.io/tx/{txn_signature}")
            logger.info(f"dexscreener https://dexscreener.com/solana/{mint}?maker={self.wallet.pubkey}")
            return True
        except Exception as e:
            logger.info(f"交易失败 {e}")
            return False

    async def sell(self, mint: Pubkey, amount: int = 0):
        try:
            if amount == 0:
                await self.wallet.update_token_accounts()
                token_data = self.wallet.get_token_accounts(mint)
                if token_data is not None:
                    mint_amount = int(token_data.amount)
                    if mint_amount <= 0:
                        logger.info(f"出售结束 {mint} 代币余额不足")
                        return False
                    txn_signature = await self._sell(mint_amount)
                    logger.info(f"出售结束 https://solscan.io/tx/{txn_signature}")
                    return True
                else:
                    logger.info(f"出售结束 {mint} 代币不存在")
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"交易失败 {e}")
            return False
