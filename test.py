import matplotlib.pyplot as plt
import ccxt

pair = 'DASH/USDT'
exchanges = [ccxt.hitbtc(), ccxt.binance(), ccxt.exmo(),
             ccxt.kucoin(), ccxt.poloniex(), ccxt.bittrex()]


def percentage(percent, whole) -> float:
    return (percent * whole) / 100.0


def display_ticker(g, p):
    bid = 0
    volume = 0
    try:
        t = g.fetch_ticker(p)
        bid = float(t['bid'])
        volume = float(t['baseVolume'])
        plt.annotate(g.id, (bid, volume))
    except ccxt.ExchangeError as e:
        print(str(e))
    except KeyError as e:
        print('pair', str(e), 'not available for', g.id)
    return bid, volume


def display_plot(gateways, p):
    plt.title(p)
    plt.xlabel('price')
    plt.ylabel('base volume')
    prices = []
    volumes = []
    for g in gateways:
        t = display_ticker(g, p)
        if t[0] == 0:
            continue
        print(g.id, t[0])
        prices.append(t[0])
        volumes.append(t[1])
        plt.scatter(t[0], t[1])
        plt.annotate(g.id, (t[0], t[1]))
    prices.sort(reverse=True)
    volumes.sort(reverse=True)
    max1 = float(prices[0])
    max2 = float(volumes[0])
    min1 = float(prices[len(prices)-1])
    min2 = float(volumes[len(prices)-1])
    top1 = float(max1 + percentage(10.0, max1))
    top2 = float(max2 + percentage(10.0, max2))
    low1 = float(min1 - percentage(5.0, min1))
    low2 = float(min2 - percentage(5.0, min2))
    plt.axis([low1, top1, low2, top2])
    plt.show()


print("plotting...")
display_plot(exchanges, pair)
