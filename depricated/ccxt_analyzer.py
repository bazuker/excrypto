import asyncio
from functools import partial

import ccxt.async as ccxt

from depricated.dealer import Dealer
from helper import load_markets


class DealAnalyzer:

    def __init__(self, gateways):
        self.gateways = gateways
        self.taker_fees = None
        self.__deals = []

    # analyzes the situation and returns the best deals
    async def compare_gateways(self, pairs, progress_callback, error_callback, deal_callback, gateway_combination):
        pairs_len = len(pairs)
        if pairs is None or pairs_len == 0:
            return None
        g1 = gateway_combination[0]
        g2 = gateway_combination[1]
        # scan all available pairs
        dealer = Dealer(g1, g2, self.taker_fees, error_callback)
        for p in pairs:
            # check if the pair is available for trading in the exchangers
            if not (p in g1.markets and p in g2.markets):
                print(p, "is not in a market of", g1.id, '/', g2.id)
                continue
            # fetch the rates
            if not await dealer.fetch_order_book(p):
                continue
            # find the deals based on retrieved data
            new_deals = dealer.produce_deals()
            if new_deals is None or len(new_deals) < 1:
                continue
            else:
                # call the deal callback asap after producing the results
                if deal_callback is not None:
                    deal_callback(new_deals)
                self.__deals.extend(new_deals)
        # update on progress
        progress_callback(g1, g2, self.__deals)
        del dealer

    # look up for the best pairs across the gateways in the provided list
    # and saves them in the local database
    # returns amount of record added to the database
    def analyze(self, pairs, progress_callback, error_callback, deal_callback=None):
        if pairs is None:
            return 0
        # load the markets if they were not loaded previously
        load = False
        for g in self.gateways:
            if g.markets is None:
                load = True
                break
        if load:
            load_markets(self.gateways)
        # load fees
        if self.taker_fees is None:
            self.taker_fees = {}
            for g in self.gateways:
                desc = g.describe()
                if 'fees' in desc:
                    self.taker_fees[g.id] = desc['fees']['trading']['taker']
                else:
                    self.taker_fees[g.id] = 0.001
        # list combinations
        compare_gateways_partial = partial(self.compare_gateways, pairs, progress_callback,
                                           error_callback, deal_callback)
        gateways_combinations = []
        for g1 in self.gateways:
            for g2 in self.gateways:
                if g1.id != g2.id:
                    t = (g1, g2)
                    gateways_combinations.append(t)
        # run the analysis asynchronously
        self.__deals.clear()
        try:
            loop = asyncio.get_event_loop()
            [asyncio.ensure_future(compare_gateways_partial(x)) for x in gateways_combinations]
            pending = asyncio.Task.all_tasks()
            loop.run_until_complete(asyncio.gather(*pending))
        except ccxt.DDoSProtection as e:
            error_callback(e, "ccxt_analyzer.analyze.DDoSProtection")
        # sort by potential profit and return the result
        self.__deals.sort(key=lambda x: x.sizemul, reverse=True)
        return self.__deals
