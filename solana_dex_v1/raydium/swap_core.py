import asyncio

from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey

from orm.crud.tasks import create_tasks_log
from settings.global_variables import GlobalVariables
from solana_dex.solana.wallet import Wallet
from solana_dex_v1.common.constants import LAMPORTS_PER_SOL
from solana_dex_v1.model.pool import PoolInfo
from solana_dex_v1.raydium.swap_utils import SwapTransactionBuilder, AccountTransactionBuilder


class SwapCore:
    def __init__(self, client: AsyncClient, wallet: Wallet, pool_info: PoolInfo, wsol_type=True,
                 compute_unit_price: int = 250000):
        self.client = client
        self.wallet = wallet
        self.pool_info = pool_info
        self.compute_unit_price = compute_unit_price
        self.wsol_type = wsol_type

    async def _buy(self, token_mint: Pubkey, amount_in: int):
        """
        购买函数
        :param token_mint: 获取的代币mint
        :param amount_in: 支付数量
        :return:
        """
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.pool_info,
                                                          self.wallet.keypair, unit_price=self.compute_unit_price)

        if self.wsol_type:
            await swap_transaction_builder.wsol_append_buy(amount_in,
                                                           not self.wallet.check_token_accounts(token_mint))
        else:
            await swap_transaction_builder.wsol_append_buy(amount_in,
                                                           not self.wallet.check_token_accounts(token_mint))
        transaction = await swap_transaction_builder.compile_versioned_transaction()
        txn_signature = (await self.client.send_transaction(transaction)).value
        logger.info(f"交易创建完成 {txn_signature}")
        resp = await self.client.confirm_transaction(
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
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.pool_info,
                                                          self.wallet.keypair, unit_price=self.compute_unit_price)

        if self.wsol_type:
            await swap_transaction_builder.wsol_append_sell(amount_in)
        else:
            await swap_transaction_builder.sol_append_sell(amount_in)
        transaction = await swap_transaction_builder.compile_versioned_transaction()
        txn_signature = (await GlobalVariables.SolaraClient.send_transaction(transaction)).value
        logger.info(f"交易创建完成 {txn_signature}")
        resp = await self.client.confirm_transaction(
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
            asyncio.create_task(create_tasks_log({
                "pubkey": self.wallet.pubkey,
                "baseMint": mint,
                "tx": txn_signature,
                "amount": str(amount),
                "status": "购买任务",
                "result": "完成"
            }))
            return True
        except Exception as e:
            logger.info(f"交易失败 {e}")
            return False

    async def sell(self, mint: Pubkey, amount: int = 0, ui_amount=""):
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
                    asyncio.create_task(create_tasks_log({
                        "pubkey": self.wallet.pubkey,
                        "baseMint": mint,
                        "tx": txn_signature,
                        "amount": str(token_data.uiAmount),
                        "status": "出售任务",
                        "result": "完成"
                    }))
                    return True
                else:
                    logger.info(f"出售结束 {mint} 代币不存在")
                    return False
            else:
                txn_signature = await self._sell(amount)
                logger.info(f"出售结束 https://solscan.io/tx/{txn_signature}")
                asyncio.create_task(create_tasks_log({
                    "pubkey": self.wallet.pubkey,
                    "baseMint": mint,
                    "tx": txn_signature,
                    "amount": str(ui_amount),
                    "status": "出售任务",
                    "result": "完成"
                }))
                return True
        except Exception as e:
            logger.error(f"交易失败 {e}")
            return False


class AccountCore:
    def __init__(self, client, wallet: Wallet):
        self.client = client
        self.wallet = wallet

    async def clone_no_balance_account(self):
        try:
            no_account = self.wallet.get_no_balance_account()
            if len(no_account) == 0:
                logger.info("没有需要清理的账户")
                return
            account_transaction_builder = AccountTransactionBuilder(GlobalVariables.SolaraClient, self.wallet.keypair)
            for account in no_account:
                account_transaction_builder.append_close_account(account)
            transaction = await account_transaction_builder.compile_versioned_transaction()
            txn_signature = (await GlobalVariables.SolaraClient.send_transaction(transaction)).value
            logger.info(f"任务创建完成 {txn_signature}")
            resp = await self.client.confirm_transaction(
                txn_signature,
                Confirmed,
            )
            return txn_signature
        except Exception as e:
            logger.error(e)
