import asyncio
import pickle

from solana_dex_v1.model.pool import PoolInfo
from solana_dex_v1.utils.client_utils import AsyncClientFactory


async def demo():
    data = {'id': 'DjUku8omwqpmMdkv9vQRbndR9zaZmsGdSadT9kTLGMb',
            'baseMint': 'A1puJVQjWaf4J5Wed3Seh21JZaRrw3nGCq6FxP2uKRfk',
            'quoteMint': 'So11111111111111111111111111111111111111112',
            'authority': '5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1',
            'openOrders': '7pGxg2MH5ECzEickY82V3i56yQq8Y1GQDoayDWPihHMx',
            'targetOrders': '6Wk5AvJCWaXpBbNe99ecPXPyryq1cdWu76wRcNXcDs1y',
            'baseVault': 'FCGNaa2WaLaMv9eBUCrNDW4MZQVWFgdPj5mcfixgz3x1',
            'quoteVault': 'm5dmTdQaeAxPTy7L1oRie6oHUu6y7cNZC1QeYCikXnu',
            'marketId': '6nzQwDCWkrWGjjtScT3TTthh9Lfntu49HDnLzB1wyryg',
            'marketBids': 'ACoRrWi6gK9hP6qMVba1KBtGqj9Pr4V6tXd19mk1Zg3M',
            'marketAsks': 'B3EgRpN6XNeXPEfhRzvoTuaEZyTVHsron34ZH1ZdzaJa',
            'marketBaseVault': 'Hyontq2ubBmFDktMK9ZbHK53tf1866S1kgRVgrVMZouW',
            'marketQuoteVault': '3Rgwci7JexW3Pv5UrEXK7b9gk1ZCj1Uz8aBAZWWfnYqB',
            'marketAuthority': 'GiWvn8PEm6WTeoFWos2anRdQ7mYk2DbmcHfjHewFxEkx',
            'marketEventQueue': 'BUv1GDCRhLJPhjzLR4dQ3Ddf3zF5kipXhytu7JSHPwj6', 'poolOpenTime': 1711586567}

    aaaa = pickle.dumps(PoolInfo(data))
    print(pickle.loads(aaaa).__dict__)


asyncio.run(demo())
