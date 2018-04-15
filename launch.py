import ccxt.async as ccxt
from bot_crawler import BotCrawler


hitbtc = ccxt.hitbtc()
binance = ccxt.binance()
kucoin = ccxt.kucoin()
poloniex = ccxt.poloniex()
bittrex = ccxt.bittrex()
exmo = ccxt.exmo()
liqui = ccxt.liqui()
gateways = [hitbtc, binance, kucoin, poloniex, bittrex, exmo, liqui]

pairs = ['BCH/USDT', 'BTC/USDT', 'LTC/USDT']
crawler = BotCrawler(gateways, pairs)
try:
    crawler.run()
except KeyboardInterrupt:
    print('stop.')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
