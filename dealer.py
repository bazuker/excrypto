from functools import partial

from exchange_data import Exchange

import ccxt.async as ccxt
import asyncio


data_cache = {}


def convert_ccxt_order_book(gateway, sym, orderbook):
    symbols = [x.strip() for x in sym.split('/')]
    asks = orderbook['asks'][0]
    bids = orderbook['bids'][0]
    ask_price = asks[0]
    ask_size = asks[1]
    bid_price = bids[0]
    bid_size = bids[1]
    return Exchange(gateway.id, ask_price, ask_size, bid_price, bid_size, symbols[0], symbols[1], gateway)


async def convert_fetch(symbol, g):
    return convert_ccxt_order_book(g, symbol, await g.fetch_order_book(symbol))


async def fetch_order_books_async(symbol, g):
    gid = g.id + symbol
    try:
        data_cache[gid] = await convert_fetch(symbol, g)
    except ccxt.ExchangeError as e:
        print('exchange error', e)
        if g.id in data_cache:
            del data_cache[gid]
    except ccxt.RequestTimeout as e:
        print('timeout', e)
        if g.id in data_cache:
            del data_cache[gid]


class Dealer:

    def __init__(self, g1, g2):
        self.g1 = g1
        self.g2 = g2
        self.e1 = None
        self.e2 = None

    def fetch_order_book(self, symbol):
        fetch_async = partial(fetch_order_books_async, symbol)
        [asyncio.ensure_future(fetch_async(g)) for g in [self.g1, self.g2]]
        pending = asyncio.Task.all_tasks()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*pending))
        gid1 = self.g1.id + symbol
        gid2 = self.g2.id + symbol
        if gid1 in data_cache and gid2 in data_cache:
            self.e1 = data_cache[gid1]
            self.e2 = data_cache[gid2]
            return True
        return False

    def produce_deals(self):
        deals = []
        rate = self.e1.compare(self.e2)
        if rate.is_profitable():
            deals.append(rate)
        rate = self.e2.compare(self.e1)
        if rate.is_profitable():
            deals.append(rate)
        return deals

