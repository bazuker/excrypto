from filtering import SymbolFilter

class DealAnalyzer:
	# analyzes the situation and returns the best deals
	def analyzeGateways(self, g1, g2, progress_callback):
		# retrieve the pairs
		g1_pairs = g1.get_pairs()
		g2_pairs = g2.get_pairs()
		# filter the pairs
		filter = SymbolFilter()
		available_pairs = filter.splitPairs(filter.matchPairs(g1_pairs, g2_pairs))
		available_pairs_len = len(available_pairs)

		# scan all available pairs
		deals = []
		n = 0
		for p in available_pairs:
			# update on progress
			n += 1	
			if progress_callback(n, available_pairs_len):
				return
			# fetch the rates
			e1 = g1.fetch(p[0], p[1]) # api request
			if e1 == None:
				continue
			e2 = g2.fetch(p[0], p[1]) # api request
			if e2 == None:
				continue
			# compare the rates
			rate = e1.compare(e2)         
			if rate.isProfitable():
				deals.append(rate)
			rate = e2.compare(e1)           
			if rate.isProfitable():
				deals.append(rate)  
		# sort by potential profit and return the result
		deals.sort(key=lambda x: x.sizemul, reverse=True)
		return deals

	# look up for the best pairs across the gateways in the provided list
	def findBestPairs(self, gateways, progress_callback):
		deals = []
		for g1 in gateways:
			for g2 in gateways:
				if g1.get_identifier() != g2.get_identifier():
					deals.extend(self.analyzeGateways(g1, g2, progress_callback))
		# fit the data into the table
		average_table = {}
		for d in deals:
			key = d.exchange1.identifier + '/' + d.exchange2.identifier + ' ' + d.exchange1.sym1 + '-' + d.exchange1.sym2
			if key in average_table:
				av = average_table[key]
				av.append(d.sizemul)
				average_table[key] = av
			else:
				average_table[key] = [d.sizemul]
		# calculate the average
		result_table = {}
		for key, value in average_table.items():
			total = 0
			for v in value:
				total += v
			total /= len(value)
			result_table[key] = total

		return result_table





