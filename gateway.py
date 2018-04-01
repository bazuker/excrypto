class CryptoGateway:
	def __init__(self):
		raise NotImplementedError('subclasses must override __init__()!')

	# must place an order
	def bid(self, sym1, sym2, side, price, amount):
		raise NotImplementedError('subclasses must override bid()!')
	
	# must fetch the ask and bid prices for the currencies
	# and return the list of Exchange objects
	def fetch(self, sym1, sym2):
		raise NotImplementedError('subclasses must override fetch()!')

	# must return a list of all possible pairs
	def get_pairs(self):
		raise NotImplementedError('subclasses must override get_pairs()!')

	# must return a unique identifier
	def get_identifier(self):
		raise NotImplementedError('subclasses must override get_identifier()!')