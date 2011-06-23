import sys

from xml.dom import minidom

from pyf2 import debug, init
from pyf2.items import props, items

global counter 
counter = 0

class Message(items.Item):
	def handle(self, input, output):
		global counter
		# if input == "read *self":
		# 	if counter < 2:
		# 		output.write("The message, neatly marked in the sawdust, reads...", False)
		# 		output.write("*** You have won ***")
		# 	else:
		# 		output.write("The message has been carelessly trampled, making it difficult to read. You can just distinguish the words...", False)
		# 		output.write("*** You have lost ***")
				

doc = minidom.parse("cod.xml")
game = init.buildGameFromXML(doc, sys.modules[__name__])

i = debug.Debugger()

i.loadGame(game)
i.run()
