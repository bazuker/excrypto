from coinapi_v1 import CoinAPIv1
from gateway import Exchange
from gateway import ExchangeRate

from kucoin_gateway import KucoinGateway

import datetime
import urllib

test_key = '78543729-3B7A-412B-B8ED-510D6B6BF6C5'
api = CoinAPIv1(test_key)

kucoin_gateway = KucoinGateway()

def fetchExchangers(limit=1):
    lst = []
    exchanges = api.metadata_list_exchanges()
    for exchange in exchanges:
        try:
            eid = exchange['exchange_id']
            print('Fetching', eid)
            book = api.orderbooks_current_data_symbol(eid + '_SPOT_BTC_USDT')    
            obj = Exchange(eid, book['asks'][0]['price'],
                               book['bids'][0]['price'],
                               book['bids'][0]['size'])                                   
            lst.append(obj)
            if len(lst) == limit:
                return lst;
        except urllib.error.HTTPError as err:
            print("Warning!", eid, " does not have a pair,", err)

    return lst


exList = fetchExchangers(5);
deals = []

# comparing
for e1 in exList:
    for e2 in exList:
        if e1.identifier != e2.identifier:
            print("---------------------------------")
            print(e1.identifier, "to", e2.identifier)

            rate = e1.compare(e2)           
            if rate.isProfitable():
                deals.append(rate)
                rate.printAll()
                #rate.exchange.gateway.bid(...)
            else:
                print("skipping")

            print("-- inverse --")
            rate = e2.compare(e1)        
            if rate.isProfitable():
                deals.append(rate)  
                rate.printAll()
                # rate.exchange.gateway.bid(...)
            else:
                print("skipping")   


print("-------------BEST DEAL--------------")
deals.sort(key=lambda x: x.sizemul, reverse=True)
print("Max sizemul", deals[0].sizemul, "to", deals[0].exchange.identifier)



