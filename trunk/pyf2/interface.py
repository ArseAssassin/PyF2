from io.output import Output

class Interface(object):
	def __init__(self):
		self.logging = True
		self.log = []
		
	def loadGame(self, game):
		self.game = game
		
	def startGame(self):
		raise Exception("Unimplemented")		
		
	def saveGameState(self):
		raise Exception("Unimplemented")
		
	def promptInput(self):
		raise Exception("Unimplemented")
		
	def input(self, s):
		prompt = self.prompt
		
		input = self.game.parse(s)
		output = self.game.handle(input)
		
		if self.logging:
			self.log.append(("%s %s" % (prompt, s), output.text))
		
		self.printOutput(output)
		
	def printOutput(self, output):
		raise Exception("Unimplemented")
		
	@property
	def prompt(self):
		return self.game.prompt
	
		
class Basic(Interface):
	def __init__(self):
		import readline
		Interface.__init__(self)
		
	def run(self):
		output = Output()
		self.game.writeIntro(output)
		self.printOutput(output)
		while True:
			self.promptInput()
	
	def printOutput(self, output):
		print output.text
		
	def promptInput(self):
		a = raw_input(self.prompt)
		self.input(a)

