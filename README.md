# excrypto

Crypto-trading bot that is able to find price spreads between currencies on different cryptocurrency trading platforms, record detected opportunities to the SQLite database and execute orders.

## Installation
The bot uses ccxt to interact with various exchangers, therefore it has to be installed beforehand
```bash
$ pip3 install ccxt
$ git clone https://github.com/kisulken/excrypto
```

## Launch
To start looking for arbitrage opportunities
```bash
$ python3 start_bot_crawler.py
```

To start executing on opportunities
```bash
$ python3 start_bot_speculator.py
```

Disclaimer: the software was created for educational purposes only and was not proven to provide income and/or not intended to be used with real assets and could potentially lead to loses of these assets. Use it only on your own risk.
