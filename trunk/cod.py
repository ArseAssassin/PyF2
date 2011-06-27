import sys

from xml.dom import minidom

from pyf2 import debug, init
from pyf2.world import props, items

from pyf2.world.events import game_events

class Message(world.Item):
	counter = 0
	
	def handle(self, input, output):
		if input == "read *self" or input == "examine *self":
			if not input.actor.has('cloak'):
				if self.counter < 2:
					output.write("The message, neatly marked in the sawdust, reads...", -1)
					self.dispatchEvent(game_events.GAME_WON())
					output.write("*** You have won! ***")
				else:
					output.write("The message has been carelessly trampled, making it difficult to read. You can just distinguish the words...", -1)
					self.dispatchEvent(game_events.GAME_LOST())
					output.write("*** You have lost! ***")
			else:
				self.counter += 1
				if self.counter == 1:
					output.write("In the dark? You could easily disturb something!")
				else:
					output.write("Blundering around in the dark isn't a good idea!")
				

doc = minidom.parse("cod.xml")
game = init.buildGameFromXML(doc, sys.modules[__name__])

i = debug.Debugger()

i.loadGame(game)
i.run()
