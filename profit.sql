SELECT count(sizemul), avg(sizemul), avg(size), avg(profit) FROM stocks 
WHERE sym1='XRP' AND sym2='BTC';

SELECT * FROM stocks 
WHERE ex2='poloniex' AND sym1='XRP'
ORDER BY sizemul desc

SELECT count(ex1), sum(sizemul), sum(size) FROM stocks 
WHERE strftime('%s', time) BETWEEN strftime('%s', '2018-05-01 00:00:01') AND strftime('%s', datetime())
AND sym1='XLM' AND sym2='BTC' 
AND profit > 0.00114569279738439
AND ex1 != 'poloniex' AND ex2 != 'poloniex'
ORDER BY sizemul DESC
