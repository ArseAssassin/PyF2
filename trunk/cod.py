import sys

from pyf2 import debug, init
from pyf2.world.items import Item

class Message(Item):
	# counter for how many times the message has been interacted with
	counter = 0 

	def handle(self, input, output):
		if input == "read *self" or input == "examine *self":
			# You can match input against raw string objects. Here we're checking
			# if player has input "read message" or "examine message". The wildcard "*self"
			# matches the object currently handling input, in this case the Message object.

			if input.actor.has('cloak'):
				# Check whether the player is carrying the cloak
			
				self.counter += 1
				if self.counter == 1:
					output.write("In the dark? You could easily disturb something!")
					# Write a message that is displayed to the player. After writing it,
					# the handling process is immediately stopped.
				else:
					output.write("Blundering around in the dark isn't a good idea!")
			else:
			
				if self.counter < 2:
					output.write("The message, neatly marked in the sawdust, reads...", 1)
					# You can define priority for each message. Higher priority messages are always 
					# displayed before lower priority messages. Output is closed after a message is
					# written with 0 priority.
				
					self.game.winGame()
					# This doesn't end the input handling process and allows you to write an outro
					# before ending the gameplay.
				
					output.write("*** You have won! ***")
				else:
					output.write("The message has been carelessly trampled, making it difficult to read. You can just distinguish the words...", 1)
					self.game.loseGame()
					output.write("*** You have lost! ***")
				

game = init.buildGameFromXML(
	init.parseXML('cod.xml'), 	# parse our world definition
	sys.modules[__name__] 		# pass the current module as argument
)

if __name__ == "__main__":
	# INTERFACE CODE
	i = debug.Debugger()
	i.loadGame(game)

	if '-p' in sys.argv or '--play' in sys.argv:
		i.run()
	else:
		i.test(
			'''
			x yourself
			n
			s
			read message
			n
			w
			x hook
			hang cloak on hook
			x hook
			e
			s
			read message
			'''
		)
		assert i.hashLog() == "1dcf7903b2184e9cadd08624e51e035fbd028ade"
		print 'Test successful'
