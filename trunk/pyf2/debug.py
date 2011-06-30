import hashlib

from io import output

from interface import Basic

class Debugger(Basic):
	def __init__(self):
		Basic.__init__(self)
		
	def printOutput(self, output):
		print output.text
		
	def run(self):
		Basic.run(self)
		
		print
		print "-"*33
		print "Hash digest for this playthrough:"
		print "-"*33
		print self.hashLog()
		
	def hashLog(self):
		f = hashlib.sha1()
		f.update(unicode(self.log))
		return f.hexdigest()
		
	def test(self, s):
		for x in s.strip().split("\n"):
			x = x.strip()
			self.printOutput(self.input(x))
		
	def promptInput(self):
		a = raw_input(self.prompt)
		if a == "debug":
			import code
		
			code.interact("PyF2 debug console\nCtrl+D to quit\n" + "-"*20, local={
				"game":self.game,
				"Output":output.Output,
				"testInput": self.testInput
			})
			
			print "Returning to normal game"
		else:
			self.printOutput(self.input(a))
			
	def input(self, s):
		prompt = self.prompt
		
		input = self.game.parse(s)
		output = self.game.handle(input)
		
		self.log.append(("%s %s" % (prompt, s), output.text))
		
		return output
	

	def testInput(self, item, input):
		o = output.Output()
		command = self.game.parse(input)
		
		try:
			item.handle(input, o)
		except output.OutputClosed:
			pass
		
		return o.text
		
		