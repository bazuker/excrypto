from gateway import CryptoGateway
from exchange_data import Exchange
from hitbtc_client import Client


class HitbtcGateway(CryptoGateway):
    def __init__(self):
        self.identifier = 'HITBTC'
        self.client = Client('https://api.hitbtc.com',
                             'ce8a6139ab24af710ab6f56ac12f3865', '2769680fde2446ca12312fcd04f15e78')
        self.pairs_cached = None

    def bid(self, sym1, sym2, side, price, amount):
        print('bidding hard!!!')

    def fetch(self, sym1, sym2):
        try:
            depth = self.client.get_orderbook(sym1 + sym2)
            bid_name = 'bid'
            ask_name = 'ask'
            if not ((bid_name in depth and len(depth[bid_name]) > 0) and
                    (ask_name in depth and len(depth[ask_name]) > 0)):
                return None
            bid = depth[bid_name][0]
            ask = depth[ask_name][0]
            return Exchange(self.identifier, float(ask['price']), float(ask['size']),
                            float(bid['price']), float(bid['size']), sym1, sym2, self)
        except:
            return None

    def get_pairs(self):
        if self.pairs_cached == None:
            tickers = self.client.session.get("%s/public/ticker" % self.client.url).json()
            pairs = []
            for t in tickers:
                pairs.append(t['symbol'])
            self.pairs_cached = pairs
        return self.pairs_cached

    def get_identifier(self):
        return self.identifier
