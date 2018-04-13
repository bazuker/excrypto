SELECT sum(sizemul) FROM stocks WHERE sym1='LTC' AND sym2='USDT' AND size < 10 AND sizemul > 15

select * from stocks where ex2='exmo' and sym2='USDT' and sizemul > 3 order by sizemul desc

select sum(sizemul) from stocks where sym2='USDT' and sizemul > 5 and size <= 0.1 order by sizemul desc
