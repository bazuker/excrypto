import ccxt.async as ccxt

from dealer import Dealer
from helper import async_list_task


async def load_markets_async(g):
    return await g.load_markets()


class DealAnalyzer:

    def __init__(self, gateways):
        self.gateways = gateways
        self.taker_fees = None

    # analyzes the situation and returns the best deals
    def compare_gateways(self, g1, g2, pairs, progress_callback, deal_callback=None):
        pairs_len = len(pairs)
        if pairs is None or pairs_len == 0:
            return None
        # scan all available pairs
        dealer = Dealer(g1, g2, self.taker_fees)
        deals = []
        n = 0
        for p in pairs:
            # check if the pair is available for trading in the exchangers
            if not (p in g1.markets and p in g2.markets):
                print(p, "is not in a market of", g1.id, '/', g2.id)
                continue
            # fetch the rates
            if not dealer.fetch_order_book(p):
                continue
            # find the deals based on retrieved data
            new_deals = dealer.produce_deals()
            # update on progress
            n += 1
            progress_callback(n, p, g1, g2, pairs_len)
            if new_deals is None or len(new_deals) < 1:
                continue
            else:
                # call the deal callback asap after producing the results
                if deal_callback is not None:
                    deal_callback(new_deals)
                deals.extend(new_deals)
            # sort by potential profit and return the result
        deals.sort(key=lambda x: x.sizemul, reverse=True)
        del dealer
        return deals

    # look up for the best pairs across the gateways in the provided list
    # and saves them in the local database
    # returns amount of record added to the database
    def analyze(self, pairs, progress_callback, comparison_callback, deal_callback=None):
        if pairs is None:
            return 0
        # load the markets if they were not loaded previously
        load = False
        for g in self.gateways:
            if g.markets is None:
                load = True
                break
        if load:
            async_list_task(load_markets_async, self.gateways)
        # load fees
        if self.taker_fees is None:
            self.taker_fees = {}
            for g in self.gateways:
                desc = g.describe()
                if 'fees' in desc:
                    self.taker_fees[g.id] = desc['fees']['trading']['taker']
                else:
                    self.taker_fees[g.id] = 0.001;
        # start the analysis
        count = 0
        for g1 in self.gateways:
            for g2 in self.gateways:
                if g1.id != g2.id:
                    try:
                        new_deals = self.compare_gateways(g1, g2, pairs, progress_callback, deal_callback)
                        comparison_callback(new_deals)
                        count += len(new_deals)
                    except ccxt.DDoSProtection as e:
                        print("DDoS protection", str(e))
                        continue
        return count
