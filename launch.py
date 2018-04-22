import asyncio
import ccxt.async as ccxt
from bot_crawler import BotCrawler

if __name__ == '__main__':
    # initialize exchangers instances
    hitbtc = ccxt.hitbtc()
    binance = ccxt.binance()
    kucoin = ccxt.kucoin()
    poloniex = ccxt.poloniex()
    bittrex = ccxt.bittrex()
    exmo = ccxt.exmo()
    liqui = ccxt.liqui()
    kraken = ccxt.kraken()
    huobi = ccxt.huobi()
    cex = ccxt.cex()
    bitfinex = ccxt.bitfinex2()
    # group them together
    gateways = [cex, binance, poloniex, bittrex, kraken, bitfinex, exmo]
    # define pairs for analysis
    pairs = ['XRP/BTC', 'XLM/BTC']
    # run the bot
    crawler = BotCrawler(gateways, pairs)
    try:
        crawler.run()
    except KeyboardInterrupt:
        print('stop.')


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
