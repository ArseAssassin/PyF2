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
		self.values = {}
		
	def __get__(self, instance, type):
		s = self.getDefault(instance)
		if instance not in self.values:
			return s
		else:
			return self.values[instance]
			
	def __set__(self, instance, value):
		self.values[instance] = value
		
	def getDefault(self, instance):
		raise Exception("unimplemented")


class Message(VarBase):
	def __init__(self, id, initial=None):
		VarBase.__init__(self)
		self.initial = initial
		self.id = id
		
	def getDefault(self, instance):
		s = instance.getXMLAttribute(self.id)
		if s:
			return s
		else:
			return self.initial


class DataMessage(VarBase):
	def __init__(self, default=None):
		VarBase.__init__(self)
		self.default = default
	
	def getDefault(self, instance):
		if instance.data:
			return instance.data
		else:
			return self.default
			
			
class GameMessage(Message):
	def __get__(self, instance, type):
		s = Message.__get__(self, instance, type)
		
		if isinstance(s, basestring):
			context = instance.game.getContext().clone()
			context.d['self'] = instance
			return context.evaluate(s)
		else:
			return s
	
	
if __name__ == "__main__":
	import unittest
	
	class TestPropList(unittest.TestCase):
		def test_fetching(self):
			p = PropList()
			property = Property()
			p.append(property)
			self.assertEquals(p.Property, property)
	
	unittest.main()
	
	