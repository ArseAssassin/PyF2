from io import output

from interface import Basic

class Debugger(Basic):
	def __init__(self):
		Basic.__init__(self)
		self.logging = True
		
	def printOutput(self, output):
		print output.text
		
	def promptInput(self):
		a = raw_input(self.prompt)
		if a == "debug":
			import code
		
			code.interact("PyF2 debug console\nCtrl+D to quit\n" + "-"*20, local={
				"game":self.game,
				"testInput": self.testInput
			})
			
			print "Returning to normal game"
		else:
			self.input(a)

	def testInput(self, item, input):
		o = output.Output()
		command = self.game.parse(input)
		
		try:
			item.handle(input, o)
		except output.OutputClosed:
			pass
		
		return o.text
		