import ccxt


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
        g2_desc = g2.describe()
        g1_fees = g1_desc['fees']['funding']['withdraw']
        g2_fees = g1_desc['fees']['funding']['deposit']
        if not (sym1 in g1_fees and sym1 in g2_fees):
            continue
        trading_fee1 = g1_desc['fees']['trading']['taker']
        trading_fee2 = g2_desc['fees']['trading']['taker']
        withdrawal_fee = g1_fees[sym1]
        deposit_fee = g2_fees[sym1]
        ask = orders1['asks'][0][0]
        buy_fee = 0#trading_fee1 * lot_price
        bid = orders2['bids'][0][0]
        transfer_amount = lot_price - buy_fee - withdrawal_fee
        sell_fee = 0#trading_fee2 * transfer_amount
        result = (((transfer_amount - sell_fee - deposit_fee) / ask) * bid) - lot_price
        t = p, result
        costs.append(t)
    costs.sort(key=lambda x: x[1], reverse=True)
    return costs





d = calc_transfer_cost(ccxt.kraken(), ccxt.binance(), "XRP", 5877)
print(d)
print("end")
