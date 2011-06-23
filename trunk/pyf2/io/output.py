from context import Context

class Output(object):
	def __init__(self, context=None):
		self.context = context
		self.output = []
		self.closed = False
		
	def write(self, s, shouldClose=True):
		self.output.append(self.evaluate(s))
		if shouldClose:
			self.close()
			
	def writeRaw(self, s):
		self.output.append(s)
		
	def close(self):
		self.closed = True
		raise OutputClosed()
		
	@property
	def text(self):
		return "\n".join(self.output)
		
	def evaluate(self, s):
		if self.context:
			return self.context.evaluate(s)
		else:
			return s
		
		
class OutputClosed(Exception):
	pass


