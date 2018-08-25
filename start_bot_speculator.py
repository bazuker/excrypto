import ccxt.async as ccxt
from bot_speculator import BotSpeculator
from helper import NoInternetException

if __name__ == '__main__':
    # initialize exchangers instances

    kraken = ccxt.kraken({'apiKey': 'yourapikey',
                          'secret': 'yoursecrect'})
    binance = ccxt.binance({'apiKey': 'yourapikey',
                            'secret': 'yoursecrect'})
    # group them together
    gateways = [binance, kraken]  #[cex, binance, bittrex, poloniex, kraken]
    # define pairs for analysis
    pairs = ['XRP/BTC']
    # run the bot
    speculator = BotSpeculator(gateways, pairs, 10.3)
    try:
        speculator.run(5)
    except KeyboardInterrupt:
        print('stop.')
    except NoInternetException:
        print('Connect to the Internet to run the program!')
