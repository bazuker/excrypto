import os
import sys
import time
from random import randint

from analyzer import DealAnalyzer
from binance_gateway import BinanceGateway
from hitbtc_gateway import HitbtcGateway
from kucoin_gateway import KucoinGateway

kucoin_gateway = KucoinGateway()
hitbtc_gateway = HitbtcGateway()
binance_gateway = BinanceGateway()


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def progress(n, p, total):
    cls()
    print('scanned', n, 'out of', total, '|', p)
    if n == total:
        print("next...")
    return False  # continue


# pairs = [['ETH', 'BTC'], ['BTC', 'ETH'], ['LTC', 'USDT'], ['USDT', 'LTC']]
analyzer = DealAnalyzer()
count = 0
try:
    while True:
        count = analyzer.analyze([kucoin_gateway, hitbtc_gateway, binance_gateway], None, progress)
        print("waiting...")
        time.sleep(randint(60, 180))

except KeyboardInterrupt:
    print('Stopped. Found', count, 'deals')
    sys.exit(0)