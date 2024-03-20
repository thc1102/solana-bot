import asyncio
import json
import time

from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair

import solana_dex.solana.client_wrapper as client_wrapper
from solana_dex.common.direction import Direction
from solana_dex.common.unit import Unit
from solana_dex.raydium_pool import RaydiumPool
from solana_dex.solana_tx_utils.swap_transaction_builder import SwapTransactionBuilder
from solana_dex.solana_util.solana_websocket_subscription import (
    subscribe_to_account_using_queue,
)


class Swap:
    def __init__(
            self,
            client: AsyncClient,
            pool: RaydiumPool,
            virtual_amount: int = 1,
            queue_size: int = 100,
            rate_limit_seconds: float = 0.1,
            rate_limit_sleep_seconds: float = 0.01,
            confirm_tx_sleep_seconds: float = 1,
    ):
        self.client = client
        self.pool = pool
        self.virtual_amount = virtual_amount
        self.queue_size = queue_size
        self.rate_limit_seconds = rate_limit_seconds
        self.rate_limit_sleep_seconds = rate_limit_sleep_seconds
        self.confirm_tx_sleep_seconds = confirm_tx_sleep_seconds
        self.price = None
        self.default_keypair = None
        # 初始化时更新本地价格
        self.update_local_price()

    async def run_updater(self):
        await asyncio.gather(
            self.update_local_price_on_changes(),
        )

    def update_local_price(self):
        # 计算价格时使用的虚拟金额
        whatever_the_amount_to_calculate = self.virtual_amount
        _, new_base_price, _, _ = self.pool.get_price(
            whatever_the_amount_to_calculate,
            Direction.SPEND_QUOTE_TOKEN,
            Unit.BASE_TOKEN,
            False,
        )
        if self.price != new_base_price:
            self.price = new_base_price

    async def update_local_price_on_changes(self, websocket_rpc_url: str = None):
        if websocket_rpc_url is None:
            # 尝试使用与客户端相同的端点
            websocket_rpc_url = self.client._provider.endpoint_uri.replace(
                "https:", "wss:"
            )
        queue = asyncio.Queue(self.queue_size)

        async def update_price(queue: asyncio.Queue):
            last_time = time.time()
            while True:
                try:
                    await queue.get()
                    while not queue.empty():
                        queue.get_nowait()
                    await self.pool.update_pool_vaults_balance(self.client.commitment)
                    self.update_local_price()
                    queue.task_done()
                    # 速率限制
                    while time.time() - last_time < self.rate_limit_seconds:
                        await asyncio.sleep(self.rate_limit_sleep_seconds)
                    last_time = time.time()
                except asyncio.CancelledError:
                    break

        await asyncio.gather(
            subscribe_to_account_using_queue(
                queue,
                websocket_rpc_url,
                self.pool.amm_id,
                self.client.commitment,
            ),
            update_price(queue),
        )

    async def buy(
            self,
            amount_in: float,
            slippage_allowance: float,
            payer: Keypair,
            update_vault: bool = True,
            confirm_commitment: str = "confirmed",
    ):
        # 获取最小输出量
        _, _, expect_amount_out, _ = self.pool.get_price(
            amount_in, Direction.SPEND_QUOTE_TOKEN, Unit.BASE_TOKEN, update_vault
        )
        amount_out = expect_amount_out * (1 - slippage_allowance)
        # 转换为交易格式
        amount_in = self.pool.convert_quote_token_amount_to_tx_format(amount_in)
        amount_out = self.pool.convert_base_token_amount_to_tx_format(amount_out)
        # 购买
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.pool, payer)
        await swap_transaction_builder.append_buy(amount_in, amount_out, True)
        transaction = swap_transaction_builder.compile_versioned_transaction()
        print(transaction)
        txn_signature = await client_wrapper.send_transaction(self.client, transaction).value
        # 等待确认
        resp = await client_wrapper.confirm_transaction(
            self.client,
            txn_signature,
            confirm_commitment,
            self.confirm_tx_sleep_seconds,
        )
        return resp

    async def sell(
            self,
            amount_in: float,
            slippage_allowance: float,
            payer: Keypair,
            update_vault: bool = True,
            confirm_commitment: str = "confirmed",
    ):
        # 获取最小输出量
        _, _, expect_amount_out, _ = self.pool.get_price(
            amount_in, Direction.SPEND_BASE_TOKEN, Unit.BASE_TOKEN, update_vault
        )
        amount_out = expect_amount_out * (1 - slippage_allowance)
        # 转换为交易格式
        amount_in = self.pool.convert_base_token_amount_to_tx_format(amount_in)
        amount_out = self.pool.convert_quote_token_amount_to_tx_format(amount_out)
        # 出售
        swap_transaction_builder = SwapTransactionBuilder(self.client, self.pool, payer)
        await swap_transaction_builder.append_sell(amount_in, amount_out)
        transaction = swap_transaction_builder.compile_versioned_transaction()
        txn_signature = await client_wrapper.send_transaction(self.client, transaction).value
        # 等待确认
        resp = await client_wrapper.confirm_transaction(
            self.client,
            txn_signature,
            confirm_commitment,
            self.confirm_tx_sleep_seconds,
        )
        return resp

    async def get_pool_lp_supply(self, signer: Keypair, commitment="confirmed"):
        swap_transaction_builder = SwapTransactionBuilder(
            self.client, self.pool, signer
        )
        await swap_transaction_builder.append_get_pool_data()
        tx = swap_transaction_builder.compile_versioned_transaction()
        simulate_result = await client_wrapper.simulate_transaction(
            self.client, tx, False, commitment
        )
        simulate_logs = simulate_result.value.logs
        pool_info_raw = ""

        program_log_expected = "Program log: GetPoolData: "

        for log in simulate_logs:
            if log.startswith(program_log_expected):
                pool_info_raw = log
                break

        if pool_info_raw == "":
            raise Exception(
                "无法获取池信息，因为找不到程序日志"
            )

        pool_info_raw = pool_info_raw.replace(program_log_expected, "")
        try:
            pool_info = json.loads(pool_info_raw)
        except:
            print("加载池 JSON 失败")
            print(simulate_logs)
            raise Exception("加载 JSON 失败")

        # pool_open_time 可能是池创建时的时间（unix 时间戳）

        lp_supply = int(pool_info["pool_lp_supply"])
        lp_supply_unlocked = int(
            await client_wrapper.get_token_supply(self.client, self.pool.lp_token_address).value.amount)
        lp_locked = lp_supply - lp_supply_unlocked

        return lp_supply, lp_locked, lp_locked / lp_supply

    async def get_pool_lp_locked_ratio(
            self, signer: Keypair, max_retry_count=0, commitment="confirmed"
    ):
        try:
            retry_count = -1
            while retry_count < max_retry_count:
                retry_count += 1
                try:
                    _, _, lp_locked_ratio = await self.get_pool_lp_supply(signer, commitment)
                    return lp_locked_ratio
                except Exception as e:
                    print(e)
                    print("无法获取池 LP 锁定比例，正在重试...")
                    continue
            raise Exception("无法获取池 LP 锁定比例")
        except:
            print("无法获取池 LP 锁定比例")
            return -1
