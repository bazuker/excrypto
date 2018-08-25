from functools import partial
from helper import async_list_task

import ccxt.async as ccxt


class BufferBook:
    def __init__(self, symbol, g, data):
        self.symbol = symbol
        self.gateway = g
        self.data = data


class OrderBookBuffer:
    def __init__(self, gateways, error_callback):
        self.data = []
        self.gateways = gateways
        self.error_callback = error_callback

    async def __fetch(self, symbol, g):
        try:
            bb = BufferBook(symbol, g, await g.fetch_order_book(symbol))
            self.data.append(bb)
        except ccxt.ExchangeError as e:
            self.error_callback(e, 'dealer.fetch_order_books_async.ExchangeError')
        except ccxt.ExchangeNotAvailable as e:
            self.error_callback(e, 'dealer.fetch_order_books_async.ExchangeNotAvailable')
        except ccxt.RequestTimeout as e:
            self.error_callback(e, 'dealer.fetch_order_books_async.RequestTimeout')

    def fetch(self, symbol):
        f = partial(self.__fetch, symbol)
        async_list_task(f, self.gateways)

