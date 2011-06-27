from base import ItemBase, PropList, Variable
from events import game_events
from scope import Scope
from errors import *

class Item(ItemBase):
	def __init__(self, xmlnode=None):
		ItemBase.__init__(self, xmlnode)
		
		self.props = PropList()
		self.inventory = []
		self.noun = None
		
	def __iter__(self):
		for x in self.noun:
			yield x
			
	@property
	def definite(self):
		return self.noun.definite

	@property
	def indefinite(self):
		return self.noun.indefinite
		
	@property
	def name(self):
		return self.noun.name
		
	@property
	def children(self):
		return self.inventory
		
	@property
	def position(self):
		scope = self.getScope()
		l = []
		for item in scope.travelUp():
			l.append(item.name)
			
		return " . ".join(l)
		
	def addProp(self, prop):
		self.props.append(prop)
		
	def removeProp(self, prop):
		self.props.remove(prop)
		
	def move(self, destination):
		if destination in self.getScope().getChildren():
			raise MoveError("Can't move to own child")
		
		self.dispatchEvent(
			game_events.MOVE(destination=destination, done=False))
			
		if destination:
			destination.dispatchEvent(
				game_events.ACQUIRE(destination=self, done=False))

		if self.owner:
			self.owner.inventory.remove(self)

		self.owner = destination

		if self.owner:
			self.owner.inventory.append(self)

		self.dispatchEvent(
			game_events.MOVE(destination=destination, done=True))
			
		if destination:
			destination.dispatchEvent(
				game_events.ACQUIRE(destination=self, done=True))


	def _handle(self, input, output):
		self.handle(input, output)
		for prop in self.props:
			prop._handle(input, output)
		
		self.owner.dispatchEvent(game_events.CHILD_HANDLE(done=True))
		
		
	def handle(self, input, output):
		pass
		
	def get(self, name):
		for item in self.inventory:
			if item == name:
				return item
				
	def __eq__(self, other):
		if self is other:
			return True
			
		if isinstance(other, Item):
			return self is other
			
		if self.noun == other:
			return True
			
		return False
		
	def getScope(self):
		return Scope(self)
		
	def has(self, other):
		return other in self.getScope().getChildren()
		

class Actor(Item):
	msg_default = Variable("msg_default", "Come again?")
	msg_unknownNoun = Variable("msg_unknownNoun", "You see nothing like that here.")
	msg_unknownVerb = Variable("msg_unknownVerb", "You don't know how to \"{{input.unknown[0].name}}\" things.")
	
	def handle(self, input, output):
		if input == ("inventory",):
			self.writeInventory(output)
		
		if input == ("*verb", "*unknown"):
			output.write(self.msg_unknownNoun)
			
		if input == ("*unknown", "*noun"):
			output.write(self.msg_unknownVerb)
		
		output.write(self.msg_default)
		
	def writeInventory(self, output):
		output.write("You're carrying:", -2)
		for item in self.inventory:
			output.write(item.indefinite, -1)
			
		output.close()
		
		
		