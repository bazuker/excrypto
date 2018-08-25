import asyncio
import time

import helper

from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import RequestTimeout
from ccxt.base.errors import ExchangeNotAvailable

from bot import Bot
from random import randint
from ccxt_buffered_analyzer import BufferedAnalyzer
from orders_history_database import OrdersHistoryDatabase
from executed_orders_history_database import ExecutedOrdersHistoryDatabase


class BotSpeculator(Bot):

    # networth in BTC
    def __init__(self, gateways, pairs, networth=10.3):
        super(BotSpeculator, self).__init__(gateways, pairs)
        self.__running = False
        self.__networth = networth
        self.__orders_history = None
        self.__executed_orders_history = None
        self.__temp_gateways = list(gateways)
        self.__balance = {}
        self.__initial_balance = {}

        self.__recovery = False  # recovery mode after a fail market order
        self.__in_transfer = False  # bot is awaiting for the transfer

        self.__buy_leftover = 0.0
        self.__sell_leftover = 0.0
        self.__avg_profit_rate = 0.0
        self.__avg_size = 0.0
        self.__min_size = 0.0

    def __init_database(self):
        if self.__orders_history is None:
            self.__orders_history = OrdersHistoryDatabase('history')  # creates a file instance
        if self.__executed_orders_history is None:
            self.__executed_orders_history = ExecutedOrdersHistoryDatabase('executed')  # creates a file instance

    def __error_callback(self, e, tag):
        print(e, 'at', tag)

    def __restore_temporary_gateways(self):
        self.__temp_gateways.clear()
        for g in self.gateways:
            self.__temp_gateways.append(g)

    @staticmethod
    async def __close_gateway_async(g):
        await g.close()

    def stop(self):
        if self.__running:
            self.__running = False
            helper.async_list_task(BotSpeculator.__close_gateway_async, self.gateways)

    async def __refresh_balance_gateway(self, g):
        try:
            b = await g.fetch_balance()
            self.__balance[g.id] = b
        except AuthenticationError as e:
            # remove the gateways from the temporary list
            if g in self.__temp_gateways:
                self.__temp_gateways.remove(g)
            print(e, 'failed to refresh the balance')

    def __refresh_balance(self):
        try:
            helper.async_list_task(self.__refresh_balance_gateway, self.gateways)
            return True
        except ExchangeError as e:
            self.__error_callback(e, 'dealer.fetch_order_books_async.ExchangeError')
        except ExchangeNotAvailable as e:
            self.__error_callback(e, 'dealer.fetch_order_books_async.ExchangeNotAvailable')
        except RequestTimeout as e:
            self.__error_callback(e, 'dealer.fetch_order_books_async.RequestTimeout')
        return False

    def __rate_profitability(self, deal):
        # btc_xrp = size * bid # 0.0000956
        transfer_fee = 0.0015  # in btc
        btc_rate = 0.041047053  # per hour
        size_rate = 188454.1  # per hour
        size_rate_in_btc = size_rate * deal.bid
        size_btc = deal.size * deal.bid
        trading_fee_btc = deal.exchange1.get_trading_fee(deal.exchange2)
        raw_sizemul = deal.sizemul + trading_fee_btc
        static_fee_factor = (transfer_fee * size_btc) / self.__networth
        total_fee = trading_fee_btc + static_fee_factor
        rate_factor = ((self.__networth * size_rate_in_btc) / btc_rate) - size_btc - total_fee
        return raw_sizemul * rate_factor

    def __rate_deals(self, deals):
        for d in deals:
            d.profit_rate = self.__rate_profitability(d)

    def __estimate_historic_values(self, symbol):
        # query the values from the database
        sql = "select avg(profit), min(size), avg(size) from stocks where sym1='" + symbol + "';"
        result = self.__orders_history.execute_sql(sql)
        if len(result) < 1 or len(result[0]) < 2:
            self.__avg_profit_rate = 0.0
            self.__avg_size = 0.0
            self.__min_size = 0.0
            return
        # set average profit rate
        if result[0][0] is not None:
            self.__avg_profit_rate = result[0][0]
        else:
            self.__avg_profit_rate = 0.0
        # set average deal size
        if result[0][1] is not None:
            self.__avg_size = result[0][1]
        else:
            self.__avg_size = 0.0
        # set minimum deal size
        if result[0][2] is not None:
            self.__min_size = result[0][2]
        else:
            self.__min_size = 0.0

    def __get_balance(self, exchange, sym, balance_type):
        return self.__balance[exchange.gateway.id][sym][balance_type]

    def __check_balance(self, deal):
        balance1 = self.__get_balance(deal.exchange2, deal.exchange1.sym2, 'total')
        balance2 = self.__get_balance(deal.exchange1, deal.exchange2.sym1, 'total')
        size2 = deal.size * deal.bid
        #if balance < self.__avg_size:
        #    return 2  # re-balancing is required
        if balance2 < deal.size or balance1 < size2:
            print(balance2, deal.size, balance1, size2)
            return 1  # not enough funds for the particular deal
        else:
            return 0  # ok
        # TODO: check the second balance

    def __request_transfer(self):
        self.__in_transfer = True
        print('transfer is requested')

    def __process_transfer(self):

        self.__in_transfer = False

    def __recover_from_failed_order(self, deal):
        gid1 = deal.exchange1.gateway.id
        gid2 = deal.exchange2.gateway.id
        # cache the old balance
        old_balance1 = self.__balance[gid1]
        old_balance2 = self.__balance[gid2]
        # refresh the balance
        self.__refresh_balance()
        # check the balances
        sym1 = deal.exchange1.sym1
        sym2 = deal.exchange1.sym2
        if sym2 not in old_balance1:
            print(sym2, 'balance of', gid1, 'is unavailable')
            return not self.__recovery
        if sym1 not in old_balance2:
            print(sym1, 'balance of', gid2, 'is unavailable')
            return not self.__recovery
        # compare the balances
        b1 = old_balance1[sym2]['total']
        b2 = self.__balance[gid1][sym2]['total']
        if b1 > b2:
            self.__buy_leftover = b1 - b2
            print('buy order went through')

        b1 = old_balance2[sym1]['total']
        b2 = self.__balance[gid2][sym1]['total']
        if b1 > b2:
            self.__sell_leftover = b1 - b2
            print('sell order went through')
        if self.__check_balance(deal) == 2:  # balance is below the average transaction size
            self.__request_transfer()
        # exit the recovery mode
        self.__recovery = False
        print('successfully recovered from failure')
        return not self.__recovery

    async def __execute_buy(self, deal):
        try:
            params = {'trading_agreement': 'agree'} if self.__requires_agreement(deal.exchange1) else {}
            result = await deal.exchange1.gateway.create_market_buy_order(deal.exchange1.get_pair_symbol(),
                                                                          deal.size, params)
            self.__executed_orders_history.add_entry('buy', result)
        except InsufficientFunds as e:
            self.__recovery = True
            print(e, 'failed to execute a buy order due to low funds')
        except ExchangeError as e:
            self.__recovery = True
            print(e, 'failed to execute a buy order')

    async def __execute_sell(self, deal):
        try:
            params = {'trading_agreement': 'agree'} if self.__requires_agreement(deal.exchange2) else {}
            result = await deal.exchange2.gateway.create_market_sell_order(deal.exchange2.get_pair_symbol(),
                                                                           deal.size, params)
            self.__executed_orders_history.add_entry('sell', result)
        except InsufficientFunds as e:
            self.__recovery = True
            print(e, 'failed to execute a buy sell order due to low funds')
        except ExchangeError as e:
            self.__recovery = True
            print(e, 'failed to execute a sell order')

    def __requires_agreement(self, e):
        return e.gateway.id == 'kraken'

    def __execute_top_orders(self, deals):
        total = 0
        successful = 0
        for d in deals:
            balance_status = self.__check_balance(d)
            if balance_status == 1:  # not enough funds for the transaction
                continue
            elif balance_status == 2:  # re-balancing is required
                self.__request_transfer()
                break
            if d.profit_rate < self.__avg_profit_rate:
                continue
            total += 1
            loop = asyncio.get_event_loop()
            asyncio.ensure_future(self.__execute_buy(d))
            asyncio.ensure_future(self.__execute_sell(d))
            pending = asyncio.Task.all_tasks()
            loop.run_until_complete(asyncio.gather(*pending))
            # check if any of the orders has failed
            if self.__recovery:
                # if recovery mode persists, then the program could not resolve it
                if not self.__recover_from_failed_order(d):
                    print('fatal error: failed to recover')
                    self.stop()
                    return successful, total
            else:
                successful += 1
            break

        return successful, total

    def run(self, min_interval=10):
        # verify the Internet connection
        # if not connected raises an error
        helper.internet()
        # initialize the sqlite database
        self.__init_database()
        # initialize the analyzer for the specified exchangers
        analyzer = BufferedAnalyzer(self.__temp_gateways)
        print('loading the markets...')
        try:
            self.__running = True
            while self.__running:
                start_time = time.time()
                self.clean_print('gathering...')
                self.__restore_temporary_gateways()
                if not self.__refresh_balance():
                    print('error: failed to refresh the balance')
                    time.sleep(15)
                self.__estimate_historic_values('XRP')
                # retrieve all the stats and produce deals
                print('analyzing...')
                deals = analyzer.analyze(self.pairs, self.__error_callback)
                self.__rate_deals(deals)
                deals.sort(key=lambda d: d.profit_rate, reverse=True)
                # execute the order
                result = self.__execute_top_orders(deals)
                print('executed', result[0], 'out of', result[1], 'top orders from', len(deals), 'possible orders')
                # store the records in the history database
                self.__orders_history.add_entries(deals)
                # output the results and wait
                elapsed_time = helper.truncate(time.time() - start_time, 2)
                print('elapsed time is', elapsed_time, 'seconds')
                # check if transfer was requested
                if self.__in_transfer:
                    print('awaiting for the transfer...')
                    self.__process_transfer()
                    break
                # ensure that the bot is still running
                if not self.__running:
                    break
                r = randint(int(elapsed_time * 2), int(elapsed_time * 4)) + min_interval
                print('waiting for', r, 'seconds...')
                time.sleep(r)
        finally:
            self.stop()

