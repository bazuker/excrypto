from gateway import CryptoGateway
from exchange_data import Exchange

from binance.client import Client


class BinanceGateway(CryptoGateway):
    def __init__(self):
        self.identifier = 'BINANCE'
        self.client = Client('gVzp6S75zS1YahebPr10Th5Dpru1jgcNXFiDmAuepaLa2TQiFAveCw1qDKhIk9Z1',
                             'l5KRJirK9simsjdiEbJnHFImahqt7UCR11xNEDVPzMgsWZac0cxjBSqE7Hcx6l1U')
        self.pairs_cached = None

    def bid(self, sym1, sym2, side, price, amount):
        print('bidding hard!!!')

    def fetch(self, sym1, sym2):
        try:
            depth = self.client.get_order_book(symbol=sym1 + sym2)
            bid_name = 'bids'
            ask_name = 'asks'
            if not ((bid_name in depth and len(depth[bid_name]) > 0) and
                    (ask_name in depth and len(depth[ask_name]) > 0)):
                return None
            buy = depth['bids'][0]  # bid
            sell = depth['asks'][0]  # ask
            return Exchange(self.identifier, float(sell[0]), float(sell[1]), float(buy[0]), float(buy[1]), sym1, sym2,
                            self)
        except:
            return None

    def get_pairs(self):
        if self.pairs_cached == None:
            tickers = self.client.get_all_tickers()
            pairs = []
            for t in tickers:
                pairs.append(t['symbol'])
            self.pairs_cached = pairs
        return self.pairs_cached

    def get_identifier(self):
        return self.identifier
