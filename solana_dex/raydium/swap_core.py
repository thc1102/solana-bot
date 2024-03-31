import asyncio
import random
import time
from typing import Optional

from jito_searcher_client import tx_to_protobuf_packet
from jito_searcher_client.generated.bundle_pb2 import Bundle
from jito_searcher_client.generated.searcher_pb2 import SendBundleRequest
from loguru import logger
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed, Commitment
from solders.pubkey import Pubkey

from orm.tasks import TasksLog
from settings.config import AppConfig
from settings.global_variables import GlobalVariables
from solana_dex.common.constants import LAMPORTS_PER_SOL
from solana_dex.model.pool import PoolInfo
from solana_dex.solana.wallet import Wallet
from solana_dex.utils.client_utils import JitoClientFactory
from solana_dex.utils.swap_utils import SwapTransactionBuilder


class SwapCore:
    def __init__(self, client: AsyncClient, wallet: Wallet, pool_info: PoolInfo = None,
                 compute_unit_price: int = 500000, wsol_type=True, jito_status=True):
        self.client = client
        self.wallet = wallet
        self.pool_info = pool_info
        self.compute_unit_price = compute_unit_price
        self.wsol_type = wsol_type
        self.jito_status = jito_status

    async def confirm_transaction(self, txn_signature, commitment: Optional[Commitment] = Processed):
        try:
            await self.client.confirm_transaction(
                txn_signature,
                commitment
            )
            return True
        except Exception as e:
            logger.error(e)
            return False

    async def _buy(self, token_mint: Pubkey, amount_in: int):
        """
        购买函数
        :param token_mint: 获取的代币mint
        :param amount_in: 支付数量
        :return:
        """
        if not self.pool_info:
            logger.info(f"必须初始化PoolInfo才可以使用")
            return
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.wallet.keypair,
                                                          unit_price=self.compute_unit_price)
        if self.wsol_type:
            swap_transaction_builder.wsol_append_buy(self.pool_info, amount_in,
                                                     not self.wallet.check_token_accounts(token_mint))
        else:
            await swap_transaction_builder.sol_append_buy(self.pool_info, amount_in,
                                                          not self.wallet.check_token_accounts(token_mint))
        if self.jito_status:
            swap_transaction_builder.append_transfer(
                random.choice(GlobalVariables.tip_payment_accounts),
                int(AppConfig.JITO_TIP_AMOUNT * LAMPORTS_PER_SOL)
            )
            transaction = await swap_transaction_builder.compile_signed_transaction()
            txn_signature = transaction.signatures[0]
            packets = [tx_to_protobuf_packet(transaction)]
            request_time = time.time()
            t = time.time()
            jito_client = await JitoClientFactory.get_shared_client(self.wallet.keypair)
            print(f"获取客户端耗时 {time.time() - t}")
            uuid_response = await jito_client.SendBundle(SendBundleRequest(bundle=Bundle(header=None, packets=packets)))
            logger.info(f"JITO RESPONSE {uuid_response.uuid} 发送耗时 {time.time() - request_time}")
        else:
            transaction = await swap_transaction_builder.compile_versioned_transaction()
            txn_signature = (await self.client.send_transaction(transaction)).value
        logger.info(f"buy {token_mint} 交易创建完成 {txn_signature}")
        return txn_signature

    async def _sell(self, amount_in: int):
        """
        购买函数
        :param amount_in: 支付数量
        :return:
        """
        if not self.pool_info:
            logger.info(f"必须初始化PoolInfo才可以使用")
            return
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.wallet.keypair,
                                                          unit_price=self.compute_unit_price)
        if self.wsol_type:
            swap_transaction_builder.wsol_append_sell(self.pool_info, amount_in)
        else:
            await swap_transaction_builder.sol_append_sell(self.pool_info, amount_in)
        if self.jito_status:
            swap_transaction_builder.append_transfer(
                random.choice(GlobalVariables.tip_payment_accounts),
                int(AppConfig.JITO_TIP_AMOUNT * LAMPORTS_PER_SOL)
            )
            transaction = await swap_transaction_builder.compile_signed_transaction()
            txn_signature = transaction.signatures[0]
            packets = [tx_to_protobuf_packet(transaction)]
            jito_client = await JitoClientFactory.get_shared_client(self.wallet.keypair)
            uuid_response = await jito_client.SendBundle(SendBundleRequest(bundle=Bundle(header=None, packets=packets)))
            logger.info(f"JITO RESPONSE {uuid_response}")
        else:
            transaction = await swap_transaction_builder.compile_versioned_transaction()
            txn_signature = (await self.client.send_transaction(transaction)).value
        logger.info(f"sell {self.pool_info.baseMint} 交易创建完成 {txn_signature}")
        return txn_signature

    async def buy(self, mint: Pubkey, amount: float):
        amount_in = int(amount * LAMPORTS_PER_SOL)
        try:
            txn_signature = await self._buy(mint, amount_in)
            asyncio.create_task(TasksLog.create(**{
                "pubkey": self.wallet.pubkey,
                "baseMint": mint,
                "tx": txn_signature,
                "amount": str(amount),
                "msg": "创建购买任务",
                "status": 1
            }))
            return txn_signature
        except Exception as e:
            logger.exception(f"buy {mint} 交易失败 {e}")
            asyncio.create_task(TasksLog.create(**{
                "pubkey": self.wallet.pubkey,
                "baseMint": mint,
                "amount": str(amount),
                "msg": "创建购买任务",
                "status": 0,
                "result": "创建购买任务失败"
            }))
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
                        asyncio.create_task(TasksLog.create(**{
                            "pubkey": self.wallet.pubkey,
                            "baseMint": mint,
                            "amount": str(amount),
                            "msg": "创建出售任务",
                            "status": 0,
                            "result": f"出售异常 代币余额不足"
                        }))
                        return False
                    txn_signature = await self._sell(mint_amount)
                    asyncio.create_task(TasksLog.create(**{
                        "pubkey": self.wallet.pubkey,
                        "baseMint": mint,
                        "tx": txn_signature,
                        "amount": str(amount),
                        "msg": "创建出售任务",
                        "status": 1
                    }))
                    return txn_signature
                else:
                    logger.info(f"出售结束 {mint} 代币不存在")
                    asyncio.create_task(TasksLog.create(**{
                        "pubkey": self.wallet.pubkey,
                        "baseMint": mint,
                        "amount": str(amount),
                        "msg": "创建出售任务",
                        "status": 0,
                        "result": f"出售异常 代币不存在"
                    }))
                    return False
            else:
                txn_signature = await self._sell(amount)
                asyncio.create_task(TasksLog.create(**{
                    "pubkey": self.wallet.pubkey,
                    "baseMint": mint,
                    "tx": txn_signature,
                    "amount": str(ui_amount),
                    "msg": "创建出售任务",
                    "status": 1,
                }))
                return txn_signature
        except Exception as e:
            logger.error(f"sell {mint} 交易失败 {e}")
            asyncio.create_task(TasksLog.create(**{
                "pubkey": self.wallet.pubkey,
                "baseMint": mint,
                "amount": str(amount),
                "msg": "创建出售任务",
                "status": 0,
                "result": f"创建出售任务失败"
            }))
            return False

    async def close_no_balance_account(self):
        # 关闭无余额账户
        try:
            no_account = self.wallet.get_no_balance_account()
            if len(no_account) == 0:
                logger.info("没有需要清理的无余额代币账户")
                return
            swap_transaction_builder = SwapTransactionBuilder(self.client, self.wallet.keypair)
            for account in no_account:
                swap_transaction_builder.append_close_account(account)
            transaction = await swap_transaction_builder.compile_versioned_transaction()
            txn_signature = (await self.client.send_transaction(transaction)).value
            logger.info(f"close_no_balance_account 任务创建完成 {txn_signature}")
            return txn_signature
        except Exception as e:
            logger.error(e)
            return False
