SELECT sum(sizemul) FROM stocks 
WHERE sym1='LTC' AND sym2='USDT' AND size < 10 AND sizemul > 15

SELECT * FROM stocks 
WHERE ex2='exmo' AND sym2='USDT' AND sizemul > 3 
ORDER BY sizemul desc

SELECT avg(sizemul) FROM stocks 
WHERE strftime('%s', time) BETWEEN strftime('%s', '2018-04-15 00:00:01') AND strftime('%s', datetime())
AND sym1='BTC' AND sym2='USDT' 
AND sizemul > 5 AND size <= 0.1 
ORDER BY sizemul DESC

SELECT sum(sizemul), sum(size) FROM stocks 
WHERE strftime('%s', time) BETWEEN strftime('%s', '2018-04-15 00:00:01') AND strftime('%s', datetime())
AND sym1='BTC' AND sym2='USDT' 
AND sizemul > 5 AND size <= 0.1 
ORDER BY sizemul DESC
