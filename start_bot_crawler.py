import ccxt.async as ccxt
from bot_crawler import BotCrawler
from helper import NoInternetException

if __name__ == '__main__':
    # initialize exchangers instances
    gateways = [ccxt.cex(), ccxt.poloniex(), ccxt.binance(), ccxt.kraken(), ccxt.bitfinex2(), ccxt.okex()]
    # define pairs for analysis
    pairs = ['XRP/BTC', 'XLM/BTC']
    # run the bot
    crawler = BotCrawler(gateways, pairs, 10.3)
    try:
        crawler.run(5)
    except KeyboardInterrupt:
        print('stop.')
    except NoInternetException:
        print('Connect to the Internet to run the program!')
