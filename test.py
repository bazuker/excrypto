import ccxt

from helper import truncate

from orders_history_database import OrdersHistoryDatabase

"""
def calc_transfer_cost(g1, g2, cur, lot_price=1):
    g1.load_markets()
    g2.load_markets()
    # match currencies
    pairs = []
    dic = {}
    for p in g1.symbols:
        dic[p] = 1
    for p in g2.symbols:
        if p in dic and cur in p:
            pairs.append(p)
    costs = []
    for p in pairs:
        sym1 = p[:3]
        orders1 = g1.fetch_order_book(p)
        orders2 = g2.fetch_order_book(p)
        g1_desc = g1.describe()
        g1_fees = g1_desc['fees']['funding']['withdraw']
        g2_fees = g1_desc['fees']['funding']['deposit']
        if not (sym1 in g1_fees and sym1 in g2_fees):
            continue
        withdrawal_fee = g1_fees[sym1]
        deposit_fee = g2_fees[sym1]
        ask = orders1['asks'][0][0]
        bid = orders2['bids'][0][0]
        transfer_amount = lot_price - withdrawal_fee
        result = (((transfer_amount - deposit_fee) / ask) * bid) - lot_price
        t = p, result
        costs.append(t)
    costs.sort(key=lambda x: x[1], reverse=True)
    return costs

# 5 hours
# 0.20523526338273 BTC
#  942270.54058755 size

btc_xrp = 0.0000956
xrp_usd = 0.894343
btc_rate = 0.041047053  # per hour
size_rate = 188454.1 * xrp_usd
avg_sizemul = 0.000124660458612618
avg_size = 1079.3715694549
g1 = ccxt.bitfinex2()
g2 = ccxt.binance()
g1_desc = g1.describe()
g2_desc = g2.describe()
g1_fees = g1_desc['fees']['funding']['withdraw']['XRP']
g2_fees = 0  # g2_desc['fees']['funding']['deposit']['XRP']   0 for binance
g1_fees_back = g1_desc['fees']['funding']['deposit']['BTC']
g2_fees_back = g2_desc['fees']['funding']['withdraw']['BTC']
xrp_transfer_fee = (g1_fees + g2_fees) * btc_xrp
btc_transfer_fee = g1_fees_back + g2_fees_back
total_fee = xrp_transfer_fee + btc_transfer_fee
print(xrp_transfer_fee, 'XRP in BTC =>')
print(btc_transfer_fee, 'BTC <=')
min_deposit = (total_fee / avg_sizemul) * avg_size
print("minimal required deposit")
print(truncate(min_deposit, 3), 'XRP')
print(truncate(min_deposit * btc_xrp, 3), 'BTC')
print(truncate(min_deposit * xrp_usd, 3), 'USD')
print()
daily_profit = (((btc_rate - total_fee) * 17)/100) * 30
print(daily_profit, "BTC")
"""
names = ['binance', 'poloniex', 'kraken', 'cex']
db = OrdersHistoryDatabase('stocks')


def estimate(d):
    sql = "select avg(profit), avg(sizemul), avg(size) from stocks where sym1='XRP' and ex1='" + d[0] + "' and ex2='" + d[1] + "';"
    result = db.execute_sql(sql)
    print('\tprofit', result[0][0])
    print('\tsizemul', result[0][1])
    print('\tsize', result[0][2])

data = []
for n1 in names:
    for n2 in names:
        if n1 != n2:
            sql = "select count(size) from stocks where sym1='XRP' and ex1='" + n1 + "' and ex2='" + n2 + "';"
            result = db.execute_sql(sql)
            t = (n1, n2, result[0][0])
            data.append(t)
            print(t)

data.sort(key=lambda x: x[2], reverse=True)
print('\nsorted\n')
for d in data:
    print(d)
    estimate(d)
    print()
