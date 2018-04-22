import ccxt.async as ccxt
from bot_crawler import BotCrawler
from helper import NoInternetException

if __name__ == '__main__':
    # initialize exchangers instances
    # hitbtc = ccxt.hitbtc()
    # kucoin = ccxt.kucoin()
    # liqui = ccxt.liqui()
    # huobi = ccxt.huobi()
    # exmo = ccxt.exmo()
    binance = ccxt.binance()
    poloniex = ccxt.poloniex()
    bittrex = ccxt.bittrex()
    kraken = ccxt.kraken()
    cex = ccxt.cex()
    bitfinex = ccxt.bitfinex2()
    # group them together
    gateways = [cex, binance, poloniex, bittrex, kraken, bitfinex]
    # define pairs for analysis
    pairs = ['XRP/BTC', 'XLM/BTC']
    # run the bot
    crawler = BotCrawler(gateways, pairs)
    try:
        crawler.run()
    except KeyboardInterrupt:
        print('stop.')
    except NoInternetException:
        print('Connect to the Internet to run the program!')

