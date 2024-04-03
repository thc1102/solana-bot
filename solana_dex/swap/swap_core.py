import random
import random
import time
from typing import Optional

from jito_searcher_client import tx_to_protobuf_packet
from jito_searcher_client.generated.bundle_pb2 import Bundle
from jito_searcher_client.generated.searcher_pb2 import SendBundleRequest
from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment, Processed
from solders.pubkey import Pubkey

from orm.crud import create_task_log
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.common.constants import LAMPORTS_PER_SOL
from solana_dex.model.pool import PoolInfo
from solana_dex.swap.wallet import Wallet
from utils.client_utils import JitoClientFactory
from utils.swap_utils import SwapTransactionBuilder


class SwapCore:
    def __init__(self, client: AsyncClient, wallet: Wallet, pool_info: PoolInfo = None,
                 compute_unit_price: int = 2500, sol_type=False, jito_status=False, is_simulate=True):
        self.client = client
        self.wallet = wallet
        self.pool_info = pool_info
        self.compute_unit_price = compute_unit_price
        self.sol_type = sol_type
        self.jito_status = jito_status
        self.is_simulate = is_simulate

    async def _send_transaction(self, swap_transaction_builder: SwapTransactionBuilder, is_buy: bool = True):
        if not self.is_simulate and self.jito_status:
            jito_tip_amount = AppConfig.JITO_BUY_TIP_AMOUNT if is_buy else AppConfig.JITO_SELL_TIP_AMOUNT
            swap_transaction_builder.append_transfer(
                random.choice(GlobalVariables.tip_payment_accounts),
                int(jito_tip_amount * LAMPORTS_PER_SOL)
            )
            transaction = await swap_transaction_builder.compile_signed_transaction()
            txn_signature = transaction.signatures[0]
            packets = [tx_to_protobuf_packet(transaction)]
            request_time = time.time()
            jito_client = await JitoClientFactory.get_shared_client(self.wallet.keypair)
            uuid_response = await jito_client.SendBundle(SendBundleRequest(bundle=Bundle(header=None, packets=packets)))
            logger.info(f"JITO RESPONSE {uuid_response.uuid} 发送耗时 {time.time() - request_time}")
        else:
            transaction = await swap_transaction_builder.compile_signed_transaction()
            txn_signature = transaction.signatures[0]
            if self.is_simulate:
                await self.client.simulate_transaction(transaction)
            else:
                transaction_bytes = transaction.serialize()
                await self.client.send_raw_transaction(transaction_bytes)
        return txn_signature

    async def _buy(self, mint: Pubkey, amount_in: int):
        """
        购买函数
        :param mint: 获取的代币mint
        :param amount_in: 支付数量
        :return:
        """
        if not self.pool_info:
            raise ValueError(f"购买失败 {mint} 必须初始化PoolInfo才可以使用")
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.wallet.keypair,
                                                          unit_price=self.compute_unit_price)

        await swap_transaction_builder.append_transaction(
            self.pool_info,
            amount_in,
            True,
            self.sol_type,
            not self.wallet.check_token_accounts(mint)
        )
        txn_signature = await self._send_transaction(swap_transaction_builder)
        logger.info(f"购买请求已发送 {mint} {txn_signature}")
        return txn_signature

    async def _sell(self, amount_in: int):
        """
        出售函数
        :param amount_in: 支付数量
        :return:
        """
        if not self.pool_info:
            raise ValueError(f"出售失败 {self.pool_info.baseMint} 必须初始化PoolInfo才可以使用")
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.wallet.keypair,
                                                          unit_price=self.compute_unit_price)
        await swap_transaction_builder.append_transaction(
            self.pool_info,
            amount_in,
            False,
            self.sol_type,
            False,
        )
        txn_signature = await self._send_transaction(swap_transaction_builder, False)
        logger.info(f"出售请求已发送 {self.pool_info.baseMint} {txn_signature}")
        return txn_signature

    async def confirm_transaction(self, txn_signature, commitment: Optional[Commitment] = Processed):
        # 查询是否上链成功
        try:
            await self.client.confirm_transaction(
                txn_signature,
                commitment
            )
            return True
        except Exception as e:
            logger.error(e)
            return False

    async def buy(self, mint: Pubkey, amount: float):
        amount_in = int(amount * LAMPORTS_PER_SOL)
        try:
            txn_signature = await self._buy(mint, amount_in)
            await create_task_log(self.wallet.pubkey, mint, str(amount), "创建购买任务完成", 1, 1, txn_signature)
            return txn_signature
        except Exception as e:
            logger.error(f"购买异常 {mint} 交易失败 {e}")
            await create_task_log(self.wallet.pubkey, mint, str(amount), "创建购买任务失败 购买异常", 0, 1)
            return False

    async def sell(self, mint: Pubkey, amount: int = 0, ui_amount: float = 0):
        try:
            if amount == 0:
                await self.wallet.update_token_accounts()
                token_data = self.wallet.get_token_accounts(mint)
                if token_data is not None:
                    mint_amount = int(token_data.amount)
                    if mint_amount <= 0:
                        logger.info(f"出售失败 {mint} 代币余额不足")
                        await create_task_log(self.wallet.pubkey, mint, "", "创建出售任务失败 代币余额不足", 0, 2)
                        return False
                    txn_signature = await self._sell(mint_amount)
                    await create_task_log(self.wallet.pubkey, mint, str(token_data.uiAmount), "创建出售任务完成", 1, 2,
                                          txn_signature)
                    return txn_signature
                else:
                    logger.info(f"出售失败 {mint} 代币不存在")
                    await create_task_log(self.wallet.pubkey, mint, "", "创建出售任务失败 代币不存在", 0, 2)
                    return False
            else:
                txn_signature = await self._sell(amount)
                await create_task_log(self.wallet.pubkey, mint, str(ui_amount), "创建出售任务完成", 1, 2, txn_signature)
                return txn_signature
        except Exception as e:
            logger.error(f"出售异常 {mint} 交易失败 {e}")
            await create_task_log(self.wallet.pubkey, mint, "", "创建出售任务失败 出售异常", 0, 2)
            return False

    async def close_no_balance_account(self):
        # 关闭无余额账户
        try:
            no_account = self.wallet.get_no_balance_account()
            if len(no_account) == 0:
                logger.info("没有需要清理的无余额代币账户")
                return False
            swap_transaction_builder = SwapTransactionBuilder(self.client, self.wallet.keypair)
            for account in no_account:
                swap_transaction_builder.append_close_account(account)
            transaction = await swap_transaction_builder.compile_signed_transaction()
            txn_signature = transaction.signatures[0]
            transaction_bytes = transaction.serialize()
            await self.client.send_raw_transaction(transaction_bytes)
            logger.info(f"close_no_balance_account 任务创建完成 {txn_signature}")
            return txn_signature
        except Exception as e:
            logger.error(e)
            return False
