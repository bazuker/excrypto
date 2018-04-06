from gateway import CryptoGateway
from exchange_data import Exchange

from kucoin.client import Client


class KucoinGateway(CryptoGateway):
    def __init__(self):
        self.identifier = 'KUCOIN'
        self.client = Client('5ab729da379b47428198a02f', '0c35723a-280c-48d6-8cbd-f679f661aab1')
        self.pairs_cached = None

    def bid(self, sym1, sym2, side, price, amount):
        print('bidding hard!!!')

    def fetch(self, sym1, sym2):
        try:
            depth = self.client.get_order_book(sym1 + '-' + sym2, limit=10)
            bid_name = 'BUY'
            ask_name = 'SELL'
            if not ((bid_name in depth and len(depth[bid_name]) > 0) and
                    (ask_name in depth and len(depth[ask_name]) > 0)):
                return None
            buy = depth[bid_name][0]  # bid
            sell = depth[ask_name][0]  # ask
            # 0 - price
            # 1 - amount
            # 2 - volume
            return Exchange(self.identifier, sell[0], sell[1], buy[0], buy[1], sym1, sym2, self)
        except:
            return None

    def get_pairs(self):
        if self.pairs_cached == None:
            tickers = self.client.get_tick()
            pairs = []
            for t in tickers:
                pairs.append(t['coinType'] + t['coinTypePair'])
            self.pairs_cached = pairs
        return self.pairs_cached

    def get_identifier(self):
        return self.identifier
