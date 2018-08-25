import exchange_data

from helper import load_markets
from order_book_buffer import OrderBookBuffer


class BufferedAnalyzer:

    def __init__(self, gateways):
        self.gateways = gateways
        self.taker_fees = None

    def __convert_ccxt_order_book(self, gateway, sym, order_book, limit=3):
        symbols = [x.strip() for x in sym.split('/')]
        asks = order_book['asks']
        bids = order_book['bids']
        m_len = min(len(asks), len(bids))
        orders = []
        n = 0
        for i in range(0, m_len):
            n += 1
            b = bids[i]
            a = asks[i]
            orders.append(exchange_data.ExchangeOrder(b[0], b[1], a[0], a[1]))
            if n == limit:
                break
        return exchange_data.Exchange(gateway.id, orders, symbols[0], symbols[1], gateway, self.taker_fees[gateway.id])

    def analyze(self, pairs, error_callback):
        if pairs is None:
            return None
        # load the markets if they were not loaded previously
        for g in self.gateways:
            if g.markets is None:
                load_markets(self.gateways)
                break
        # load fees
        if self.taker_fees is None:
            self.taker_fees = {}
            for g in self.gateways:
                desc = g.describe()
                if 'fees' in desc:
                    self.taker_fees[g.id] = desc['fees']['trading']['taker']
                else:
                    self.taker_fees[g.id] = 0.001
        # buffer all the rates for the given moment
        buffer = OrderBookBuffer(self.gateways, error_callback)
        exchanges = []
        deals = []
        for p in pairs:
            buffer.fetch(p)
        for book in buffer.data:
            exchanges.append(self.__convert_ccxt_order_book(book.gateway, book.symbol, book.data))
        for e1 in exchanges:
            for e2 in exchanges:
                if e1.can_compare(e2):
                    rate = e1.compare(e2)
                    if rate.is_profitable():
                        deals.append(rate)
        deals.sort(key=lambda x: x.sizemul, reverse=True)
        return deals
