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

from settings.global_variables import GlobalVariables
from solana_dex.common.constants import LAMPORTS_PER_SOL, SOL_MINT_ADDRESS, TOKEN_PROGRAM_ID
from solana_dex.raydium.models import ApiPoolInfo
from solana_dex.raydium.swap_util import make_swap_instruction
from solana_dex.solana.solana_client import SolanaRPCClient
from solana_dex.solana.wallet import Wallet


class SwapCore:
    def __init__(self, wallet: Wallet, pool_info: ApiPoolInfo, compute_unit_price: int = 250000):
        self.wallet = wallet
        self.pool_info = pool_info
        self.compute_unit_price = compute_unit_price

    async def _buy(self, token_mint: Pubkey, amount_in: int,
                   check_associated_token_account_exists=True):
        """
        购买函数
        :param token_mint: 获取的代币mint
        :param amount_in: 支付数量
        :param check_associated_token_account_exists: 检查关联的令牌帐户是否存在
        :return:
        """
        # 定义instructions存储要发送的内容
        # 接收的地址计算
        dest_address = get_associated_token_address(self.wallet.pubkey, token_mint)
        balance_needed = await AsyncToken.get_min_balance_rent_for_exempt_for_account(GlobalVariables.SolaraClient)
        new_pair_pk, swap_tx, payer, new_pair, opts, = _TokenCore._create_wrapped_native_account_args(
            TOKEN_PROGRAM_ID, self.wallet.pubkey, self.wallet.keypair, amount_in,
            False, balance_needed, Commitment("confirmed"))
        swap_tx.add(set_compute_unit_price(self.compute_unit_price))
        if str(swap_tx.recent_blockhash) == "11111111111111111111111111111111":
            recent_blockhash = await SolanaRPCClient.get_latest_blockhash()
            swap_tx.recent_blockhash = recent_blockhash
        # 判断钱包是否存在 存在则不生成创建钱包指令
        if check_associated_token_account_exists and not self.wallet.check_token_accounts(token_mint):
            # 创建关联指令
            instructions_swap_creat_associated = create_associated_token_account(
                self.wallet.pubkey, self.wallet.pubkey, token_mint
            )
            swap_tx.add(instructions_swap_creat_associated)
        # 生成swap交换指令
        instructions_swap = make_swap_instruction(amount_in, new_pair_pk, dest_address, payer.pubkey(),
                                                  self.pool_info)
        swap_tx.add(instructions_swap)
        # 创建关闭账户
        params = CloseAccountParams(account=new_pair_pk, dest=payer.pubkey(), owner=payer.pubkey(),
                                    program_id=TOKEN_PROGRAM_ID)
        close_acc = (close_account(params))
        swap_tx.add(close_acc)
        compiled_message = swap_tx.compile_message()
        transaction = VersionedTransaction(compiled_message, [payer, new_pair])
        txn_signature = (await GlobalVariables.SolaraClient.send_transaction(transaction)).value
        logger.info(f"交易创建完成 {txn_signature}")
        resp = await GlobalVariables.SolaraClient.confirm_transaction(
            txn_signature,
            Confirmed,
        )
        return txn_signature

    async def _sell(self, source_mint: Pubkey, dest_mint: Pubkey, amount_in: int):
        """
        购买函数
        :param source_mint: 支付的代币mint
        :param dest_mint: 获取的代币mint
        :param amount_in: 支付数量
        :param check_associated_token_account_exists: 检查关联的令牌帐户是否存在
        :return:
        """
        # 定义instructions存储要发送的内容
        instructions = []
        # 支付的地址计算
        source_address = get_associated_token_address(self.wallet.pubkey, source_mint)
        # 接收的地址计算
        dest_address = get_associated_token_address(self.wallet.pubkey, dest_mint)
        instructions.append(set_compute_unit_price(self.compute_unit_price))
        # 生成swap交换指令
        instructions_swap = make_swap_instruction(amount_in, source_address, dest_address, self.wallet.pubkey,
                                                  self.pool_info)
        instructions.append(instructions_swap)
        # 获取最新哈希地址
        recent_blockhash = await SolanaRPCClient.get_latest_blockhash()
        # 编译发送要发送的消息
        compiled_message = MessageV0.try_compile(
            self.wallet.pubkey,
            instructions,
            [],  # lookup tables
            recent_blockhash,
        )
        transaction = VersionedTransaction(compiled_message, [self.wallet.keypair])
        txn_signature = (await SolanaRPCClient.send_transaction(transaction)).value
        logger.info(f"交易创建完成 {txn_signature}")
        resp = await SolanaRPCClient.confirm_transaction(
            txn_signature,
            Confirmed,
        )
        return txn_signature

    async def _sell1(self, token_mint: Pubkey, amount_in: int):
        """
        购买函数
        :param token_mint: 获取的代币mint
        :param amount_in: 支付数量
        :return:
        """

        # 定义instructions存储要发送的内容
        CreateAccountWithSeedParams(from_pubkey=Pubkey("YOUR_FROM_PUBKEY"),
                                    to_pubkey=Pubkey.create_with_seed("YOUR_BASE_PUBKEY", "YOUR_SEED", "PROGRAM_ID"),
                                    base=Pubkey("YOUR_BASE_PUBKEY"),
                                    seed="YOUR_SEED",
                                    lamports=1000000,
                                    space=1024,
                                    owner=Pubkey("PROGRAM_ID"))
        # 接收的地址计算
        dest_address = get_associated_token_address(self.wallet.pubkey, token_mint)
        balance_needed = await AsyncToken.get_min_balance_rent_for_exempt_for_account(GlobalVariables.SolaraClient)
        create_account_with_seed()
        new_pair_pk, swap_tx, payer, new_pair, opts, = _TokenCore._create_wrapped_native_account_args(
            TOKEN_PROGRAM_ID, self.wallet.pubkey, self.wallet.keypair, amount_in,
            False, balance_needed, Commitment("confirmed"))
        swap_tx.add(set_compute_unit_price(self.compute_unit_price))
        if str(swap_tx.recent_blockhash) == "11111111111111111111111111111111":
            recent_blockhash = await SolanaRPCClient.get_latest_blockhash()
            swap_tx.recent_blockhash = recent_blockhash
        # 判断钱包是否存在 存在则不生成创建钱包指令
        if check_associated_token_account_exists and not self.wallet.check_token_accounts(token_mint):
            # 创建关联指令
            instructions_swap_creat_associated = create_associated_token_account(
                self.wallet.pubkey, self.wallet.pubkey, token_mint
            )
            swap_tx.add(instructions_swap_creat_associated)
        # 生成swap交换指令
        instructions_swap = make_swap_instruction(amount_in, new_pair_pk, dest_address, payer.pubkey(),
                                                  self.pool_info)
        swap_tx.add(instructions_swap)
        # 创建关闭账户
        params = CloseAccountParams(account=new_pair_pk, dest=payer.pubkey(), owner=payer.pubkey(),
                                    program_id=TOKEN_PROGRAM_ID)
        close_acc = (close_account(params))
        swap_tx.add(close_acc)
        compiled_message = swap_tx.compile_message()
        transaction = VersionedTransaction(compiled_message, [payer, new_pair])
        txn_signature = (await GlobalVariables.SolaraClient.send_transaction(transaction)).value
        logger.info(f"交易创建完成 {txn_signature}")
        resp = await GlobalVariables.SolaraClient.confirm_transaction(
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
                    txn_signature = await self._sell(mint, SOL_MINT_ADDRESS, mint_amount)
                    logger.info(f"出售结束 https://solscan.io/tx/{txn_signature}")
                    return True
                else:
                    logger.info(f"出售结束 {mint} 代币不存在")
                    return False
            else:
                return False
        except Exception as e:
            logger.exception(f"交易失败 {e}")
            return False
