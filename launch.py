import ccxt.async as ccxt
from bot_crawler import BotCrawler

# initialize exchangers instances
hitbtc = ccxt.hitbtc()
binance = ccxt.binance()
kucoin = ccxt.kucoin()
poloniex = ccxt.poloniex()
bittrex = ccxt.bittrex()
exmo = ccxt.exmo()
liqui = ccxt.liqui()
# group them together
gateways = [hitbtc, binance, kucoin, poloniex, bittrex, exmo]
# define pairs for analysis
pairs = ['BCH/USDT', 'BTC/USDT', 'LTC/USDT']
# run the bot
crawler = BotCrawler(gateways, pairs)
try:
    crawler.run()
except KeyboardInterrupt:
    print('stop.')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
