from context import Context

class Output(object):
	def __init__(self, context=None):
		self.context = context
		self.output = []
		self.closed = False
		
	def write(self, s, priority=0):
		self.output.append([self.evaluate(s), priority])
		if priority == 0:
			self.close()
			
	def writeRaw(self, s, priority=0):
		self.output.append([s, priority])
		
	def close(self):
		self.closed = True
		raise OutputClosed()
		
	@property
	def text(self):
		return "\n".join([x[0] for x in sorted(self.output, key=lambda x:x[1])])
		
	def evaluate(self, s):
		if self.context:
			return self.context.evaluate(s)
		else:
			return s
			
	def clean(self):
		self.closed = False
		self.output = []
		
		
class OutputClosed(Exception):
	pass


