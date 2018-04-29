SELECT sum(sizemul) FROM stocks 
WHERE sym1='LTC' AND sym2='USDT' AND size < 10 AND sizemul > 15

SELECT * FROM stocks 
WHERE ex2='exmo' AND sym2='USDT' AND sizemul > 3 
ORDER BY sizemul desc

SELECT sum(sizemul), sum(size) FROM stocks 
WHERE strftime('%s', time) BETWEEN strftime('%s', '2018-04-27 00:00:01') AND strftime('%s', datetime())
AND sym1='XRP' AND sym2='BTC' 
AND profit > 0.00114569279738439
ORDER BY sizemul DESC
