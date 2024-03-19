import asyncio

from solana.rpc.commitment import Commitment
from solana.rpc.websocket_api import SolanaWsClientProtocol, connect
from solders.pubkey import Pubkey


async def subscribe_to_account_using_queue(
        queue: asyncio.Queue,  # 异步队列，用于存储订阅的响应数据
        websocket_rpc_url: str,  # WebSocket RPC 的 URL
        pub_key: Pubkey,  # 要订阅的账户的公钥
        commitment: Commitment,  # 订阅的确认程度
):
    websocket: SolanaWsClientProtocol
    async with connect(websocket_rpc_url) as websocket:  # 与 WebSocket 连接
        # 发送账户订阅请求
        await websocket.account_subscribe(pub_key, commitment, "jsonParsed")
        # 接收订阅成功的响应
        response = await websocket.recv()
        subscription_id = response[0].result  # 订阅ID
        while True:
            try:
                # 接收新的响应
                response = await websocket.recv()
                if queue.full():
                    # 若队列已满，移除最旧的数据
                    try:
                        queue.get_nowait()
                    except:
                        # 若队列为空，则不做处理
                        pass
                # 将响应数据放入队列中
                await queue.put(response)
            except asyncio.CancelledError:
                break  # 若任务被取消，则退出循环
            except:
                break  # 处理其他异常情况，退出循环
        # 取消账户订阅
        await websocket.account_unsubscribe(subscription_id)


async def subscribe_to_account_using_yield(
        websocket_rpc_url: str,  # WebSocket RPC 的 URL
        pub_key: Pubkey,  # 要订阅的账户的公钥
        commitment: Commitment,  # 订阅的确认程度
):
    websocket: SolanaWsClientProtocol
    async with connect(websocket_rpc_url) as websocket:  # 与 WebSocket 连接
        # 发送账户订阅请求
        await websocket.account_subscribe(pub_key, commitment)
        # 接收订阅成功的响应
        response = await websocket.recv()
        subscription_id = response[0].result  # 订阅ID
        while True:
            try:
                # 接收新的响应
                response = await super(SolanaWsClientProtocol, websocket).recv()
                yield response  # 生成器，每次产生一个响应
            except:
                break  # 处理异常情况，退出循环
        # 取消账户订阅
        await websocket.account_unsubscribe(subscription_id)
