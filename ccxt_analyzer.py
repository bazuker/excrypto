import ccxt.async as ccxt
import asyncio

from dealer import Dealer


class DealAnalyzer:

    def __init__(self, gateways):
        self.gateways = gateways
        self.markets = None

    async def load_market_async(self, g):
        self.markets[g.id] = await g.load_markets()

    def load_markets(self):
        self.markets = {}
        [asyncio.ensure_future(self.load_market_async(g)) for g in self.gateways]
        pending = asyncio.Task.all_tasks()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*pending))

    def pair_in_market(self, g, pair):
        return g.id in self.markets and pair in self.markets[g.id]

    # analyzes the situation and returns the best deals
    def compare_gateways(self, g1, g2, pairs, progress_callback, deal_callback=None):
        pairs_len = len(pairs)
        if pairs is None or pairs_len == 0:
            return None
        # scan all available pairs
        dealer = Dealer(g1, g2)
        deals = []
        n = 0
        for p in pairs:
            # check if the pair is available for trading in the exchangers
            if not (self.pair_in_market(g1, p) and self.pair_in_market(g2, p)):
                # print(p, "is not in a market of", g1.id, '/', g2.id)
                continue
            # fetch the rates
            if not dealer.fetch_order_book(p):
                continue
            # find the deals based on retrieved data
            new_deals = dealer.produce_deals()
            if new_deals is None or len(new_deals) < 1:
                continue
            else:
                # call the deal callback asap after producing the results
                if deal_callback is not None:
                    deal_callback(new_deals)
                deals.extend(new_deals)
            # update on progress
            n += 1
            if progress_callback(n, p, g1, g2, pairs_len):
                return
            # sort by potential profit and return the result
        deals.sort(key=lambda x: x.sizemul, reverse=True)
        return deals

    # look up for the best pairs across the gateways in the provided list
    # and saves them in the local database
    # returns amount of record added to the database
    def analyze(self, pairs, progress_callback, comparison_callback, deal_callback=None):
        if pairs is None:
            return 0
        if self.markets is None:
            self.load_markets()
        count = 0
        # start the analysis
        for g1 in self.gateways:
            for g2 in self.gateways:
                if g1.id != g2.id:
                    try:
                        new_deals = self.compare_gateways(g1, g2, pairs, progress_callback, deal_callback)
                        comparison_callback(new_deals)
                        count += len(new_deals)
                    except ccxt.DDoSProtection:
                        continue
        return count
