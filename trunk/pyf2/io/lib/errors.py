class MatchingError(Exception):
	pass
	
class DisambiguationError(Exception):
	def __init__(self, msg, input, options):
		Exception.__init__(self, msg)
		
		self.input = input
		self.options = options
