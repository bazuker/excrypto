import time

from helper import truncate


class ExchangeOrder:
    def __init__(self, bid=None, bid_size=None, ask=None, ask_size=None):
        self.bid = bid
        self.bid_size = bid_size
        self.ask = ask
        self.ask_size = ask_size


class ExchangeRate:
    def __init__(self, comparison_result=None, fallback_comparison_result=None,
                 exchanger1=None, exchanger2=None):
        self.bid = comparison_result[0]
        self.bid_fallback = fallback_comparison_result[0]
        self.ask = comparison_result[1]
        self.ask_fallback = fallback_comparison_result[1]
        self.dif = comparison_result[2]
        self.dif_fallback = fallback_comparison_result[2]
        self.size = comparison_result[3]
        self.size_fallback = fallback_comparison_result[3]
        self.sizemul = comparison_result[4]
        self.sizemul_fallback = fallback_comparison_result[4]
        self.profit = self.sizemul / (self.bid * self.size)
        self.profit_fallback = self.sizemul_fallback / (self.bid_fallback * self.size)
        self.exchange1 = exchanger1
        self.exchange2 = exchanger2
        self.timestamp = time.time()

    def is_profitable(self):
        return self.sizemul > 0

    def can_fallback(self):
        return self.sizemul_fallback > 0

    def print(self):
        print("bid", "{0:.15f}".format(round(self.bid, 15)))
        print("bid_fallback", "{0:.15f}".format(round(self.bid_fallback, 15)))
        print("ask", "{0:.15f}".format(round(self.ask, 15)))
        print("ask_fallback", "{0:.15f}".format(round(self.ask_fallback, 15)))
        if self.is_profitable():
            print("dif", "{0:.15f}".format(round(self.dif, 15)))
            print("size", "{0:.15f}".format(round(self.size, 15)))
            print("sizemul", "{0:.15f}".format(round(self.sizemul, 15)))
            print("profit", "{0:.15f}".format(round(self.profit, 15)))
        if self.can_fallback():
            print("dif_fallback", "{0:.15f}".format(round(self.dif_fallback, 15)))
            print("size_fallback", "{0:.15f}".format(round(self.size_fallback, 15)))
            print("sizemul_fallback", "{0:.15f}".format(round(self.sizemul_fallback, 15)))
            print("profit_fallback", "{0:.15f}".format(round(self.profit_fallback, 15)))


class Exchange:
    def __init__(self, identifier=None, orders=None, sym1=None, sym2=None, gateway=None, fee=None):
        self.identifier = identifier  # exchanger api identifier
        self.gateway = gateway  # exchanger api gateway
        self.orders = orders
        self.sym1 = sym1
        self.sym2 = sym2
        self.fee = fee

    def __compare(self, self_order, ex_order, ex_fee):
        # difference in ask/bid between two exchanges
        dif = self_order.bid - ex_order.ask
        # minimal trading size
        min_size = min(self_order.bid_size, ex_order.ask_size)
        # deal's total
        delta = min_size * dif
        # subtract fees
        fee = float(self_order.bid * self.fee) + float(ex_order.ask * ex_fee)
        delta -= fee
        # potential profit
        sizemul = truncate(delta, 14)
        return self_order.bid, ex_order.ask, dif, min_size, sizemul

    def compare(self, ex):
        # get the top order
        self_order1 = self.orders[0]
        ex_order1 = ex.orders[0]
        # calculate profitability
        result = self.__compare(self_order1, ex_order1, ex.fee)
        # get the second top order
        self_order2 = self.orders[1]
        ex_order2 = ex.orders[1]
        # calculate the fallback profitability
        fallback_result = self.__compare(self_order2, ex_order2, ex.fee)
        # produce the exchange rate
        return ExchangeRate(result, fallback_result, self, ex)

    def print(self):
        print("identifier", self.identifier)
        print("orders", "{0:.15f}".format(round(self.orders, 15)))
        print("sym1", "{0:.15f}".format(round(self.sym1, 15)))
        print("sym2", "{0:.15f}".format(round(self.sym2, 15)))
