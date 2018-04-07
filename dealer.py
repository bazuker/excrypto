from exchange_data import Exchange


def convert_ccxt_orderbook(gateway, sym, orderbook):
    symbols = [x.strip() for x in sym.split('/')]
    asks = orderbook['asks'][0]
    bids = orderbook['bids'][0]
    ask_price = asks[0]
    ask_size = asks[1]
    bid_price = bids[0]
    bid_size = bids[1]
    return Exchange(gateway.id, ask_price, ask_size, bid_price, bid_size, symbols[0], symbols[1], gateway)


class Dealer:

    def __init__(self, g1, g2):
        self.g1 = g1
        self.g2 = g2
        self.e1 = None
        self.e2 = None

    def fetch_orderbook(self, sym):
        self.e1 = convert_ccxt_orderbook(self.g1, sym, self.g1.fetch_order_book(sym))
        self.e2 = convert_ccxt_orderbook(self.g2, sym, self.g2.fetch_order_book(sym))

    def produce_deals(self):
        deals = []
        rate = self.e1.compare(self.e2)
        if rate.is_profitable():
            deals.append(rate)
        rate = self.e2.compare(self.e1)
        if rate.is_profitable():
            deals.append(rate)
        return deals

