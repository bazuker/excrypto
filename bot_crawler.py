import time
import sqlite3
import helper

from random import randint
from ccxt_buffered_analyzer import BufferedAnalyzer
from bot import Bot


class BotCrawler(Bot):

    # networth in BTC
    def __init__(self, gateways, pairs, networth=10.3):
        super(BotCrawler, self).__init__(gateways, pairs)
        self.__conn = None
        self.__c = None
        self.__running = False
        self.networth = networth

    @staticmethod
    async def close_gateway_async(g):
        await g.close()

    def stop(self):
        if self.__running:
            self.__running = False
            helper.async_list_task(BotCrawler.close_gateway_async, self.gateways)

    def __rate_profitability(self, deal):
        # btc_xrp =  size * bid # 0.0000956
        transfer_fee = 0.0015  # in btc
        btc_rate = 0.041047053  # per hour
        size_rate = 188454.1  # per hour
        size_rate_in_btc = size_rate * deal.bid
        size_btc = deal.size * deal.bid
        trading_fee_btc = deal.exchange1.get_trading_fee(deal.exchange2)
        raw_sizemul = deal.sizemul + trading_fee_btc
        static_fee_factor = (transfer_fee * size_btc) / self.networth
        total_fee = trading_fee_btc + static_fee_factor
        rate_factor = ((self.networth * size_rate_in_btc) / btc_rate) - size_btc - total_fee
        return raw_sizemul * rate_factor

    def __init_database(self):
        # create a local database
        self.__conn = sqlite3.connect('stocks.db')
        self.__c = self.__conn.cursor()
        self.__c.execute('''CREATE TABLE IF NOT EXISTS stocks (time datetime, ex1 text, ex2 text, sym1 text, 
        sym2 text, bid real, ask real, size real, sizemul real, profit real, fallback boolean)''')

    def __analyze(self, new_deals):
        if new_deals is None or len(new_deals) < 1:
            return
        t = []
        for d in new_deals:
            ex1 = d.exchange1
            ex2 = d.exchange2
            profit_rate = self.__rate_profitability(d)
            tup = (ex1.identifier, ex2.identifier, ex1.sym1, ex1.sym2,
                   d.bid, d.ask, d.size, d.sizemul, profit_rate, d.can_fallback())
            t.append(tup)
        try:
            self.__c.executemany('INSERT INTO stocks VALUES(datetime(),?,?,?,?,?,?,?,?,?,?)', t)
            self.__conn.commit()
        except sqlite3.OperationalError as e:
            print("database error:", str(e))

    def __error_callback(self, e, tag):
        print(e, 'at', tag)

    def run(self, min_interval=10):
        # verify the Internet connection
        # if not connected raises an error
        helper.internet()
        # initialize the sqlite database
        self.__init_database()
        # initialize the analyzer for the specified exchangers
        analyzer = BufferedAnalyzer(self.gateways)
        print('loading markets...')
        try:
            self.__running = True
            while self.__running:
                start_time = time.time()
                deals = analyzer.analyze(self.pairs, self.__error_callback)
                self.__analyze(deals)
                elapsed_time = helper.truncate(time.time() - start_time, 2)
                self.clean_print("elapsed time is", elapsed_time, "seconds")
                print("detected", len(deals), "deals this round")
                r = randint(int(elapsed_time * 2), int(elapsed_time * 4)) + min_interval
                print("waiting", r, 'seconds...')
                time.sleep(r)
        finally:
            self.stop()
            self.__conn.close()

