from base import Property, Message, DataMessage, GameMessage
from events import game_events
from events.game_events import *

class Surface(Property):
	msg_hang = Message("msg_hang", "You hang {{input.noun.definite}} on {{input.nouns[1].definite}}.")
	msg_put = Message("msg_put", "You place {{input.noun.definite}} on {{input.nouns[1].definite}}.")
	hanger = GameMessage("hanger", False)
	
	def handle(self, input, output):
		if self.hanger:
			if input == ("hang", "*noun", "on", "*self"):
				input.item.move(self.owner)
				output.write(self.msg_hang)
				
		elif input == ("put", "*noun", "on", "*self"):
			input.item.move(self.owner)
			output.write(self.msg_put)


class Container(Property):
	msg_put = Message("msg_put", "You finish placing {{input.noun.definite}} in {{self.owner.definite}}.")
	msg_alreadyPut = Message("msg_alreadyPut", "{{input.noun.definite}} is already in {{self.owner.definite}}.")
	
	def handle(self, input, output):
		if input == ("put", "*noun", "in", "*self"):
			input.noun.item.move(self.owner)
			output.write(self.msg_put)
			
			
class Dark(Property):
	msg_dark = Message("msg_dark", "You can't do that in the dark.")
	msg_dark_description = Message("msg_dark_description", "It's dark in here.")
	lit = GameMessage("lit", False)
	
	def assignParent(self, parent):
		Property.assignParent(self, parent)
		self.owner.addEventListener(CHILD_HANDLE, self.onChildHandle)
		self.owner.addEventListener(DESCRIBE, self.onDescribe)
		
	def onDescribe(self, event):
		if not self.lit:
			self.requestHandling(lambda input, output: output.write(self.msg_dark_description))
		
	def onChildHandle(self, event):
		if not self.lit:
			self.requestHandling(self.outputMessage)
			
	def outputMessage(self, input, output):
		output.write(self.msg_dark)


class Closable(Property):
	TRY_OPEN = GameEvent("try_open")
	
	msg_closed = Message("msg_closed", "You finish closing {{self.owner.definite}}.")
	msg_alreadyClosed = Message("msg_alreadyClosed", "{{self.owner.definite}} is already closed.")

	msg_open = Message("msg_open", "You finish opening {{self.owner.definite}}.")
	msg_alreadyOpen = Message("msg_alreadyOpen", "{{self.owner.definite}} is already open.")

	isClosed = Message("isClosed", False)
	
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
	
	key = Message("key", None)
	msg_locked = Message("msg_locked", "{{self.owner.definite}} is locked.")
	msg_unlocked = Message("msg_unlocked", "You finish unlocking {{self.owner.definite}}.")
	isLocked = Message("isLocked", False)
	
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
	description = DataMessage("No description.")
	
	def handle(self, input, output):
		if input == ("examine", "*self"):
			output.write(self.description)


Desc = Describable # shortcut for Describable


class Wearable(Property):
	msg_wear = Message("msg_wear", "You finish putting on {{input.noun.definite}}.")
	msg_first = Message("msg_first", "(first taking {{input.noun.definite}} off)")
	msg_alreadyWorn = Message("msg_worn", "You're already wearing {{input.noun.definite}}.")

	msg_strip = Message("msg_strip", "You finish taking off {{input.noun.definite}}.")
	msg_alreadyStripped= Message("msg_stripped", "You're not wearing {{input.noun.definite}}.")

	msg_notCarrying = Message("msg_notCarrying", "You're not carrying {{input.noun.definite}}.")
	
	worn = GameMessage("worn", False)

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
	msg_tooHot = Message("msg_tooHot", "{{input.noun.definite}} is too hot to touch.")
	isHot = Message("isHot", False)
	
	def handle(self, input, output):
		if input == ("*touch", "*self") and self.isHot:
			output.write(self.msg_tooHot)
				

TAKE = GameEvent("take")
DROP = GameEvent("drop")

class Portable(Property):
	msg_dropped = Message("msg_dropped", "You drop {{input.noun.definite}} on the ground.")
	isDroppable = Message("isDroppable", True)
	
	msg_taken = Message("msg_taken", "You pick up {{input.noun.definite}}.")
	isPortable = Message("isPortable", True)
	
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
	input = Message("input")
	output = DataMessage()
	
	def handle(self, input, output):
		if input == self.input:
			output.write(self.output)
			
			
class Traversable(Property):
	msg_noExit = Message("msg_noExt", "There is no exit leading that way.")
	
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
	description = DataMessage("No description.")

	def handle(self, input, output):
		if input == ("examine",) or input == "":
			self.writeDescription(output)
			
	def writeDescription(self, output):
		output.write(self.item.name, 1)
		self.owner.dispatchEvent(game_events.DESCRIBE())
		output.write(self.description, 1)
		
		moved = filter(lambda x: x.props.Portable and x.props.Portable.moved, self.item.inventory)
		if moved:
			output.write("You can also see %s here." % ', '.join([item.noun.indefinite for item in moved]), 1)
			
		output.close()
			
			
class Throwable(Property):
	msg_hits = Message("msg_hits", "{{input.noun.definite}} hits {{input.nouns[1].definite}} and drops on the ground.")
	msg_notCarried = Message("msg_notCarried", "You're not carrying {{input.noun.definite}}.")
	
	def handle(self, input, output):
		if input == ("throw", '*self', 'at', '*noun'):
			if self.item.owner != input.actor:
				output.write(self.msg_notCarried)
			else:
				input.item.move(input.items[1].owner)
				output.write(self.msg_hits)


class Unreachable(Property):
	msg_unreachable = Message("msg_hits", "{{input.noun.definite}} is out of your reach.")
	isReachable = GameMessage("isReachable", False)
	
	def handle(self, input, output):
		if input == ("*touch", "*self"):
			if not self.isReachable:
				output.write(self.msg_unreachable)


class Seat(Property):
	msg_sat = Message("msg_sat", "You take a seat on {{input.noun.definite}}.")
	msg_stood = Message("msg_satOn", "You stand up.")
	msg_inlineStood = Message("msg_satOn", "(first standing up)")
	msg_notFree = Message("msg_satOn", "That seat is already taken.")

	sitter = GameMessage("sitter", None)
	
	def handle(self, input, output):
		if input == ('sit', 'on', '*self'):
			if self.sitter != None:
				output.write(self.msg_notFree)
			else:
				self.assignSitter(input.actor)
				output.write(self.msg_sat)
				
	def assignSitter(self, actor):
		self.sitter = actor
		actor.addEventListener(game_events.ACT, onAct)
		self.sitter.addEventListener(game_events.MOVE, onSitterMove)
		
	def removeSitter(self):
		self.sitter.removeEventListener(game_events.MOVE, onSitterMove)
		self.sitter = None
		
	def onAct(self, event):
		if event.input == ("stand", "up") or event.input == ("stand", ):
			removeSitter()
			event.output.write(self.msg_stood)
	
	def onSitterMove(self, event):
		self.removeSitter()
		event.output.write(self.msg_inlineStood, 1)
		
		
