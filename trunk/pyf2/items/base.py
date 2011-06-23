from events import events, game_events
from xmlinit import nodes, errors
from errors import PropError

class ItemBase(nodes.XMLINode, events.EventDispatcher):
	def __init__(self, xmlnode=None):
		events.EventDispatcher.__init__(self)
		if xmlnode:
			self.initXML(xmlnode)
	
	def initXML(self, node):
		nodes.XMLINode.__init__(self, node)
		
	@property
	def game(self):
		return self.owner.game
		
	def requestHandling(self, function):
		self.dispatchEvent(game_events.REQUEST_HANDLING(function))


class Property(ItemBase):
	@property
	def item(self):
		return self.owner
		
	def _handle(self, input, output):
		self.handle(input, output)
		
	def handle(self, input, output):
		pass
		
	def assignParent(self, parent):
		if self.owner != None:
			raise errors.ParentError()
		self.owner = parent
		
		self.owner.addProp(self)
		

class PropList(list):
	def __getattr__(self, name):
		for x in self:
			if x.__class__.__name__ == name:
				return x
			
		return	
		raise PropError("No prop named %s found" % name)

class VarBase(object):
	def __init__(self):
		self.overridden = False
		
	def __get__(self, instance, type):
		s = self.getDefault(instance)
		if s and not self.overridden:
			return s
		else:
			return self.value
			
	def __set__(self, instance, value):
		self.overridden = True
		self.value = value
		
	def getDefault(self, instance):
		raise Exception("unimplemented")


class Variable(VarBase):
	def __init__(self, id, initial=None):
		VarBase.__init__(self)
		self.value = initial
		self.id = id
		
	def getDefault(self, instance):
		return instance.getXMLAttribute(self.id)


class DataVariable(VarBase):
	def __init__(self, default=None):
		VarBase.__init__(self)
		self.default = default
	
	def getDefault(self, instance):
		if instance.data:
			return instance.data
		else:
			return self.default
			
			
class GameVariable(Variable):
	def __get__(self, instance, type):
		s = Variable.__get__(self, instance, type)
		if isinstance(s, basestring):
			return instance.game.getContext().evaluate(s)
	