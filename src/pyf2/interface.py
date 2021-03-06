from io.output import Output
from world.events import game_events

class Interface(object):
	def __init__(self):
		self.log = []
		self.game = None
		self.gameFinished = False
		
	def loadGame(self, game):
		if self.game:
			self.game.removeEventListener(game_events.GAME_WON, self.onVictory)
			self.game.removeEventListener(game_events.GAME_LOST, self.onDefeat)			
		
		self.game = game
		self.game.addEventListener(game_events.GAME_WON, self.onVictory)
		self.game.addEventListener(game_events.GAME_LOST, self.onDefeat)
		
	def onVictory(self, event):
		raise Exception("Unimplemented")		

	def onDefeat(self, event):
		raise Exception("Unimplemented")		
		
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
		
		output.write(self.game.title, 1)
		output.write("A game by %s" % self.game.author, 1)
		
		self.printOutput(output)
		try:
			while not self.gameFinished:
				self.promptInput()
		except KeyboardInterrupt, e:
			pass
		except EOFError, e:
			pass
	
	def printOutput(self, output):
		print output.text
		
	def promptInput(self):
		a = raw_input(self.prompt)
		self.input(a)

	def onVictory(self, event):
		self.gameFinished = True

	def onDefeat(self, event):
		self.gameFinished = True

