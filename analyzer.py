import sqlite3
import sys
import os

from filtering import SymbolFilter


class DealAnalyzer:
    def __init__(self):
        self.symbolFilter = SymbolFilter()

    # returns matching pairs
    def match_gateways_pairs(self, g1, g2):
        return self.symbolFilter.split_pairs(self.symbolFilter.match_pairs(g1.get_pairs(), g2.get_pairs()))

    # analyzes the situation and returns the best deals
    def analyze_gateways(self, g1, g2, pairs, progress_callback):
        pairs_len = len(pairs)
        if pairs is None or pairs_len == 0:
            pairs = self.match_gateways_pairs(g1, g2)
            pairs_len = len(pairs)
        # scan all available pairs
        deals = []
        n = 0
        for p in pairs:
            # update on progress
            n += 1
            if progress_callback(n, p, pairs_len):
                return
            # fetch the rates
            e1 = g1.fetch(p[0], p[1])  # api request
            if e1 is None:
                continue
            e2 = g2.fetch(p[0], p[1])  # api request
            if e2 is None:
                continue
            # compare the rates
            rate = e1.compare(e2)
            if rate.is_profitable():
                deals.append(rate)
            rate = e2.compare(e1)
            if rate.is_profitable():
                deals.append(rate)
            # sort by potential profit and return the result
        deals.sort(key=lambda x: x.sizemul, reverse=True)
        return deals

    # look up for the best pairs across the gateways in the provided list
    # and saves them in the local database
    # returns amount of record added to the database
    def analyze(self, gateways, pairs, progress_callback):
        if pairs is None:
            pairs = []
        # create a local database
        conn = sqlite3.connect('stocks.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS stocks (time datetime, ex1 text, ex2 text, sym1 text, 
sym2 text, bid real, ask real, size real, sizemul real)''')
        count = 0
        try:
            # start the analysis
            for g1 in gateways:
                for g2 in gateways:
                    if g1.get_identifier() != g2.get_identifier():
                        t = []
                        new_deals = self.analyze_gateways(g1, g2, pairs, progress_callback)
                        for d in new_deals:
                            ex1 = d.exchange1
                            ex2 = d.exchange2
                            tup = (ex1.identifier, ex2.identifier, ex1.sym1, ex1.sym2, d.bid, d.ask, d.size, d.sizemul)
                            t.append(tup)
                        c.executemany('INSERT INTO stocks VALUES(datetime(),?,?,?,?,?,?,?,?)', t)
                        conn.commit()
                        count += len(new_deals)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
        finally:
            conn.close()
        return count
