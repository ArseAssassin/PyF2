from base import Property, Variable, DataVariable, GameVariable
from events import game_events
from events.game_events import *

class Surface(Property):
	msg_hang = Variable("msg_hang", "You hang {{input.noun.definite}} on {{input.nouns[1].definite}}.")
	msg_put = Variable("msg_put", "You place {{input.noun.definite}} on {{input.nouns[1].definite}}.")
	hanger = GameVariable("hanger", False)
	
	def handle(self, input, output):
		if self.hanger:
			if input == ("hang", "*noun", "on", "*self"):
				input.item.move(self.owner)
				output.write(self.msg_hang)
				
		elif input == ("put", "*noun", "on", "*self"):
			input.item.move(self.owner)
			output.write(self.msg_put)


class Container(Property):
	msg_put = Variable("msg_put", "You finish placing {{input.noun.definite}} in {{self.owner.definite}}.")
	msg_alreadyPut = Variable("msg_alreadyPut", "{{input.noun.definite}} is already in {{self.owner.definite}}.")
	
	def handle(self, input, output):
		if input == ("put", "*noun", "in", "*self"):
			input.noun.item.move(self.owner)
			output.write(self.msg_put)
			
			
class Dark(Property):
	msg_dark = Variable("msg_dark", "It's too dark to do that here.")
	lit = GameVariable("lit", False)
	
	def assignParent(self, parent):
		Property.assignParent(self, parent)
		self.owner.addEventListener(CHILD_HANDLE, self.onChildHandle)
		
	def onChildHandle(self, event):
		if not self.lit:
			self.requestHandling(self.outputMessage)
			
	def outputMessage(self, input, output):
		output.write(self.msg_dark)


class Closable(Property):
	TRY_OPEN = GameEvent("try_open")
	
	msg_closed = Variable("msg_closed", "You finish closing {{self.owner.definite}}.")
	msg_alreadyClosed = Variable("msg_alreadyClosed", "{{self.owner.definite}} is already closed.")

	msg_open = Variable("msg_open", "You finish opening {{self.owner.definite}}.")
	msg_alreadyOpen = Variable("msg_alreadyOpen", "{{self.owner.definite}} is already open.")

	isClosed = Variable("isClosed", False)
	
	def assignParent(self, parent):
		Property.assignParent(self, parent)
		self.owner.addEventListener(events.CHILD_ACCESS, self.onChildAccess)
		
	def onChildAccess(self, event):
		if self.isClosed:
			event.output.write(msg_closed)
			
	def handle(self, input, output):
		if input == ("open", "*self"):
			if self.isClosed:
				self.dispatchEvent(Closable.TRY_OPEN(output, False))
				self.isClosed = False
				output.write(msg_open)
				self.dispatchEvent(Closable.TRY_OPEN(output, True))
			else:
				output.write(msg_alreadyOpen)
		elif input == ("close", "*self"):
			if not self.isClosed:
				self.isClosed = True
				output.write(msg_closed)
			else:
				output.write(msg_alreadyClosed)
	

class Lockable(Property):
	
	key = Variable("key", None)
	msg_locked = Variable("msg_locked", "{{self.owner.definite}} is locked.")
	msg_unlocked = Variable("msg_unlocked", "You finish unlocking {{self.owner.definite}}.")
	isLocked = Variable("isLocked", False)
	
	def assignParent(self, parent):
		Property.assignParent(self, parent)
		self.owner.addEventListener(Closable.TRY_OPEN, self.onTryOpen)
		
	def onTryOpen(self, event):
		if self.isLocked:
			event.output.write(msg_locked)
		
	def handle(self, input, output):
		if input == ("unlock", "*self") or input == ("unlock", "*self", "with", self.key.noun):
			self.isLocked = False
			output.write(self.msg_unlocked)
			

class Describable(Property):
	description = DataVariable("No description.")
	
	def handle(self, input, output):
		if input == ("examine", "*self"):
			output.write(self.description)


Desc = Describable # shortcut for Describable


class Wearable(Property):
	msg_wear = Variable("msg_wear", "You finish putting on {{input.noun.definite}}.")
	msg_first = Variable("msg_first", "(first taking {{input.noun.definite}} off)")
	msg_alreadyWorn = Variable("msg_worn", "You're already wearing {{input.noun.definite}}.")

	msg_strip = Variable("msg_strip", "You finish taking off {{input.noun.definite}}.")
	msg_alreadyStripped= Variable("msg_stripped", "You're not wearing {{input.noun.definite}}.")

	msg_notCarrying = Variable("msg_notCarrying", "You're not carrying {{input.noun.definite}}.")
	
	worn = GameVariable("worn", False)

	def assignParent(self, parent):
		Property.assignParent(self, parent)
		self.owner.addEventListener(game_events.MOVE, self.onMove)
		
	def onMove(self, event):
		if self.worn:
			self.requestHandling(self.inlineStrip)
			
	def inlineStrip(self, input, output):
		self.worn = False
		output.write(self.msg_first, 1)

	def handle(self, input, output):
		if input == ("wear", "*self"):
			if self.item.owner != input.actor:
				output.write(self.msg_notCarrying)
				
			if self.worn:
				output.write(self.msg_alreadyWorn)
			else:
				self.worn = True
				output.write(self.msg_wear)
				
		elif input == ("strip", "*self"):
			if not self.worn:
				output.write(self.msg_alreadyStripped)
			else:
				self.worn = False
				output.write(self.msg_strip)
				
				
class Hot(Property):
	msg_tooHot = Variable("msg_tooHot", "{{input.noun.definite}} is too hot to touch.")
	isHot = Variable("isHot", False)
	
	def handle(self, input, output):
		if input == ("*touch", "*self") and self.isHot:
			output.write(self.msg_tooHot)
				

TAKE = GameEvent("take")
DROP = GameEvent("drop")

class Portable(Property):
	msg_dropped = Variable("msg_dropped", "You drop {{input.noun.definite}} on the ground.")
	isDroppable = Variable("isDroppable", True)
	
	msg_taken = Variable("msg_taken", "You pick up {{input.noun.definite}}.")
	isPortable = Variable("isPortable", True)
	
	moved = True
	
	def handle(self, input, output):
		if self.isPortable and input == ("take", "*self"):
			self.dispatchEvent(TAKE())
			input.item.move(input.actor)
			
			output.write(self.msg_taken)
			
			self.moved = True
		elif self.isDroppable and input == ("drop", "*self"):
			self.dispatchEvent(DROP())
			input.item.move(input.actor.owner)
			
			output.write(self.msg_dropped)
			
			self.moved = True
			
			
class Handler(Property):
	input = Variable("input")
	output = DataVariable()
	
	def handle(self, input, output):
		if input == self.input:
			output.write(self.output)
			
			
class Traversable(Property):
	msg_noExit = Variable("msg_noExt", "There is no exit leading that way.")
	
	def __init__(self, *args, **kwargs):
		Property.__init__(self, *args, **kwargs)
		self.shouldTraverse = False
	
	def handle(self, input, output):
		for node in self.xmlnode.childNodes:
			if node.nodeType == 1: # node is element node
				if input == (node.localName,):
					room = self.game.find(node.firstChild.nodeValue)
					input.actor.move(room)
			
					room.props.Room.writeDescription(output)
					
		if input == ("*direction",):
			output.write(self.msg_noExit)
		
		
class Room(Property):
	description = DataVariable("No description.")

	def handle(self, input, output):
		if input == ("examine",) or input == "":
			self.writeDescription(output)
			
	def writeDescription(self, output):
		output.write(self.item.name, 1)
		output.write(self.description, 1)
		
		moved = filter(lambda x: x.props.Portable and x.props.Portable.moved, self.item.inventory)
		if moved:
			output.write("You can also see %s here." % ', '.join([item.noun.indefinite for item in moved]), 1)
			
		output.close()
			
			
		