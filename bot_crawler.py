import time
import sqlite3

from random import randint
from ccxt_analyzer import DealAnalyzer
from bot import Bot
from helper import internet
from helper import async_list_task


class BotCrawler(Bot):

    def __init__(self, gateways, pairs):
        super(BotCrawler, self).__init__(gateways, pairs)
        self.__conn = None
        self.__c = None

    async def __stop_async(self, g):
        await g.close()

    def stop(self):
        async_list_task(self.__stop_async, self.gateways)

    def __init_database(self):
        # create a local database
        self.__conn = sqlite3.connect('stocks.db')
        self.__c = self.__conn.cursor()
        self.__c.execute('''CREATE TABLE IF NOT EXISTS stocks (time datetime, ex1 text, ex2 text, sym1 text, 
        sym2 text, bid real, ask real, size real, sizemul real, profit real, fallback boolean)''')

    def __insert_records(self, new_deals):
        if new_deals is None or len(new_deals) < 1:
            return
        t = []
        for d in new_deals:
            ex1 = d.exchange1
            ex2 = d.exchange2
            tup = (ex1.identifier, ex2.identifier, ex1.sym1, ex1.sym2,
                   d.bid, d.ask, d.size, d.sizemul, d.profit, d.can_fallback())
            t.append(tup)
        try:
            self.__c.executemany('INSERT INTO stocks VALUES(datetime(),?,?,?,?,?,?,?,?,?,?)', t)
            self.__conn.commit()
        except sqlite3.OperationalError as e:
            print("database error:", str(e))

    def run(self):
        # verify the Internet connection
        # if not connected raises an error
        internet()
        # initialize the sqlite database
        self.__init_database()
        # initialize the analyzer for the specified exchangers
        analyzer = DealAnalyzer(self.gateways)
        print('loading markets...')
        try:
            while True:
                count = analyzer.analyze(self.pairs, BotCrawler.progress_callback, self.__insert_records)
                print("totally added", count, "deals this round")
                r = randint(60, 120)
                print("waiting", r, 'seconds...')
                time.sleep(r)
        finally:
            self.__conn.close()

