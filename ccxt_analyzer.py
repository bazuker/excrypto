import sqlite3
import sys
import os
from dealer import Dealer
from ccxt.async import ExchangeError

class DealAnalyzer:

    # analyzes the situation and returns the best deals
    def compare_gateways(self, g1, g2, pairs, progress_callback):
        pairs_len = len(pairs)
        if pairs is None or pairs_len == 0:
            return None
        # scan all available pairs
        dealer = Dealer(g1, g2)
        deals = []
        n = 0
        for p in pairs:
            # fetch the rates
            if not dealer.fetch_order_book(p):
                continue
            # update on progress
            n += 1
            if progress_callback(n, p, g1, g2, pairs_len):
                return
            # find the deals based on retrieved data
            new_deals = dealer.produce_deals()
            if new_deals is None or len(new_deals) < 1:
                continue
            else:
                deals.extend(new_deals)
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
                    if g1.id != g2.id:
                        t = []
                        new_deals = self.compare_gateways(g1, g2, pairs, progress_callback)
                        if new_deals is None or len(new_deals) < 1:
                            continue
                        for d in new_deals:
                            ex1 = d.exchange1
                            ex2 = d.exchange2
                            tup = (ex1.identifier, ex2.identifier, ex1.sym1, ex1.sym2, d.bid, d.ask, d.size, d.sizemul)
                            t.append(tup)
                        c.executemany('INSERT INTO stocks VALUES(datetime(),?,?,?,?,?,?,?,?)', t)
                        conn.commit()
                        count += len(new_deals)

        finally:
            conn.close()
        return count
