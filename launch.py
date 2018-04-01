from exchange_data import Exchange
from exchange_data import ExchangeRate

from kucoin_gateway import KucoinGateway
from hitbtc_gateway import HitbtcGateway
# from binance_gateway import BinanceGateway

from analyzer import DealAnalyzer

import io, os, json, sys, codecs, time

kucoin_gateway = KucoinGateway()
hitbtc_gateway = HitbtcGateway()
# binance_gateway = BinanceGateway()

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def progress(n, total):
	cls()
	print('scanned', n, 'out of', total)
	if n == total:
		print("next gateway...")
	return False # continue

sym1 = 'ETH'
sym2 = 'BTC'
	
while True:
	e1 = kucoin_gateway.fetch(sym1, sym2)
	if e1 == None:
		sys.exit('kucoin fetch is null')
	
	e2 = hitbtc_gateway.fetch(sym1, sym2)
	if e2 == None:
		sys.exit('hitbtc fetch is null')

	rate = e1.compare(e2)           
	if rate.isProfitable():
		rate.printAll()
		#rate.exchange.gateway.bid(...)
	else:
		print("skipping")

	print("-- inverse --")

	rate = e2.compare(e1)        
	if rate.isProfitable():
		rate.printAll()
		# rate.exchange.gateway.bid(...)
	else:
		print("skipping")
		
	try:
		time.sleep(5)
	except KeyboardInterrupt:
		sys.exit('goodbye!')
		
	print('-----------------------')

"""
analyzer = DealAnalyzer()
pairs = analyzer.findBestPairs([kucoin_gateway, hitbtc_gateway], progress)
print("detected", len(pairs), "pairs")
print("serializing...")
with open('pairs.json', 'w') as f:
	json.dump(pairs, fp=f, sort_keys=True, indent=4, ensure_ascii=False)
for key, value in pairs.items():
        print(key, "{0:.15f}".format(round(value, 15))) 


top_deals_limit = 5
print("-------------TOP", top_deals_limit, "DEAL--------------")
for d in deals:
	print(d.exchange.sym1 + '-' + d.exchange.sym2, "sizemul", d.sizemul, "on", d.exchange.identifier)
	top_deals_limit -= 1
	if top_deals_limit == 0:
		break
"""
