import os
import sys
import time
import ccxt.async as ccxt

from random import randint
from ccxt_analyzer import DealAnalyzer


def clean_print(*args):
    os.system('cls' if os.name == 'nt' else 'clear')
    print(*args)


def progress(n, p, g1, g2, total):
    if n == 1:
        clean_print(g1.id, "/", g2.id)
    print(n, 'out of', total, '|', p)
    return False  # continue


hitbtc = ccxt.hitbtc()
binance = ccxt.binance()
kucoin = ccxt.kucoin()
poloniex = ccxt.poloniex()
bittrex = ccxt.bittrex()
gateways = [bittrex, hitbtc, binance, kucoin, poloniex]

pairs = ['LTC/BTC', 'LTC/USDT',
         'ETH/USDT', 'ETH/BTC',
         'XMR/BTC', 'ETC/ETH']
analyzer = DealAnalyzer()
count = 0
try:
    while True:
        count = analyzer.analyze(gateways, pairs, progress)
        print("added", count, "deals. Waiting...")
        time.sleep(randint(60, 180))

except KeyboardInterrupt:
    print('Stopped. Found', count, 'deals')
    sys.exit(0)