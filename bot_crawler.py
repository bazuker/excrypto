import time
import sqlite3

from random import randint
from ccxt_analyzer import DealAnalyzer
from bot import Bot


class BotCrawler(Bot):

    def __init__(self, gateways, pairs):
        super(BotCrawler, self).__init__(gateways, pairs)
        self.__conn = None
        self.__c = None

    def __init_database(self):
        # create a local database
        self.__conn = sqlite3.connect('stocks.db')
        self.__c = self.__conn.cursor()
        self.__c.execute('''CREATE TABLE IF NOT EXISTS stocks (time datetime, ex1 text, ex2 text, sym1 text, 
        sym2 text, bid real, ask real, size real, sizemul real, fallback boolean)''')

    def __insert_records(self, new_deals):
        if new_deals is None or len(new_deals) < 1:
            return
        t = []
        for d in new_deals:
            ex1 = d.exchange1
            ex2 = d.exchange2
            tup = (ex1.identifier, ex2.identifier, ex1.sym1, ex1.sym2,
                   d.bid, d.ask, d.size, d.sizemul, d.can_fallback())
            t.append(tup)
        self.__c.executemany('INSERT INTO stocks VALUES(datetime(),?,?,?,?,?,?,?,?,?)', t)
        self.__conn.commit()

    def run(self):
        self.__init_database()
        analyzer = DealAnalyzer(self.gateways)
        print('loading markets...')
        analyzer.load_markets()
        try:
            while True:
                try:
                    count = analyzer.analyze(self.pairs, BotCrawler.progress_callback, self.__insert_records)
                    print("totally added", count, "deals this round")
                except Exception as e:
                    print("error", str(e))
                r = randint(60, 120)
                print("waiting", r, 'seconds...')
                time.sleep(r)
        finally:
            self.__conn.close()

