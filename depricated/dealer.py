from exchange_data import Exchange
from exchange_data import ExchangeOrder

import ccxt.async as ccxt


class Dealer:

    def __init__(self, g1, g2, fees, error_callback):
        self.g1 = g1
        self.g2 = g2
        self.fees = fees
        self.e1 = None
        self.e2 = None
        self.data_cache = {}
        self.error_callback = error_callback

    def convert_ccxt_order_book(self, gateway, sym, order_book, limit=3):
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
            orders.append(ExchangeOrder(b[0], b[1], a[0], a[1]))
            if n == limit:
                break
        return Exchange(gateway.id, orders, symbols[0], symbols[1], gateway, self.fees[gateway.id])

    async def convert_fetch(self, symbol, g):
        return self.convert_ccxt_order_book(g, symbol, await g.fetch_order_book(symbol))

    def del_cache(self, gid):
        if gid in self.data_cache:
            del self.data_cache[gid]

    async def fetch_order_books_async(self, symbol, g):
        gid = g.id + symbol
        try:
            self.data_cache[gid] = await self.convert_fetch(symbol, g)
        except ccxt.ExchangeError as e:
            self.del_cache(gid)
            self.error_callback(e, 'dealer.fetch_order_books_async.ExchangeError')
        except ccxt.ExchangeNotAvailable as e:
            self.del_cache(gid)
            self.error_callback(e, 'dealer.fetch_order_books_async.ExchangeNotAvailable')
        except ccxt.RequestTimeout as e:
            self.del_cache(gid)
            self.error_callback(e, 'dealer.fetch_order_books_async.RequestTimeout')

    async def fetch_order_book(self, symbol):
        # fetch_async = partial(self.fetch_order_books_async, symbol)
        # async_list_task(fetch_async, [self.g1, self.g2])
        await self.fetch_order_books_async(symbol, self.g1)
        await self.fetch_order_books_async(symbol, self.g2)
        gid1 = self.g1.id + symbol
        gid2 = self.g2.id + symbol
        if gid1 in self.data_cache and gid2 in self.data_cache:
            self.e1 = self.data_cache[gid1]
            self.e2 = self.data_cache[gid2]
            return True
        return False

    def produce_deals(self):
        deals = []
        rate = self.e1.compare(self.e2)
        if rate.is_profitable():
            deals.append(rate)
        # rate = self.e2.compare(self.e1)
        # if rate.is_profitable():
        #    deals.append(rate)
        return deals
