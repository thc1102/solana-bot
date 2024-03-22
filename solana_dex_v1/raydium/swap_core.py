from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.message import MessageV0
from solders.pubkey import Pubkey
from solders.token.associated import get_associated_token_address
from solders.transaction import VersionedTransaction

from solana_dex_v1.common.constants import LAMPORTS_PER_SOL
from solana_dex_v1.raydium.models import ApiPoolInfo
from solana_dex_v1.raydium.swap_util import make_swap_instruction
from solana_dex_v1.solana.solana_client import SolanaRPCClient


class SwapCore:

    @staticmethod
    async def buy(source_mint: Pubkey, dest_mint: Pubkey, amount: float, payer: Keypair, pool_info: ApiPoolInfo):
        """
        购买函数
        :param source_mint: 支付的代币mint
        :param dest_mint: 获取的代币mint
        :param amount: 数量
        :param payer: 用户私钥
        :param pool_info: 流动池信息
        :return:
        """
        # 计算付款金额
        amount_in = int(amount * LAMPORTS_PER_SOL)
        # 支付的token计算
        source = get_associated_token_address(payer.pubkey(), source_mint)
        # 获取的token计算
        dest = get_associated_token_address(payer.pubkey(), dest_mint)
        instructions_swap = make_swap_instruction(amount_in, source, dest, payer.pubkey(), pool_info)
        print(source, dest)
        print(instructions_swap)
        recent_blockhash = await SolanaRPCClient.get_latest_blockhash()
        print(recent_blockhash)
        compiled_message = MessageV0.try_compile(
            payer.pubkey(),
            [instructions_swap],
            [],  # lookup tables
            recent_blockhash,
        )
        transaction = VersionedTransaction(compiled_message, [payer])
        print(transaction)
        print("发送成功")
        txn_signature = (await SolanaRPCClient.send_transaction(transaction)).value
        resp = await SolanaRPCClient.confirm_transaction(
            txn_signature,
            Confirmed,
        )
        print(resp)
        return resp

    @staticmethod
    async def sell(source_mint: Pubkey, dest_mint: Pubkey, amount, payer: Keypair, pool_info: ApiPoolInfo):
        """
        购买函数
        :param source_mint: 支付的代币mint
        :param dest_mint: 获取的代币mint
        :param amount: 数量
        :param payer: 用户私钥
        :param pool_info: 流动池信息
        :return:
        """
        # 计算付款金额
        amount_in = int(amount * LAMPORTS_PER_SOL)
        # 支付的token计算
        source = get_associated_token_address(payer.pubkey(), source_mint)
        # 获取的token计算
        dest = get_associated_token_address(payer.pubkey(), dest_mint)
        instructions_swap = make_swap_instruction(amount_in, source, dest, payer.pubkey(), pool_info)
        print(instructions_swap)
