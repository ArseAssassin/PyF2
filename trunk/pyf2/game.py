from errors import StateError, GameError
import states

from items.xmlinit import nodes
from items.base import ItemBase

from items.events.events import EventDispatcher
import io.lib.defaults
from io.lib import lib
from io.output import Output
from io.context import Context

class Game(ItemBase):
	def __init__(self, *args, **kwargs):
		ItemBase.__init__(self, *args, **kwargs)
		
		self.lib = self.getLib()
		self.inventory = []
		self._states = []
		
		self.title = "undefined"
		self.version = "undefined"
		self.description = "undefined"
		self.introduction = "undefined"
		
		self.shouldTraverse = True
		
		self.owner = None
		
	@property
	def game(self):
		return self
		
	@property
	def children(self):
		return []
		
	def addItem(self, item):
		if item in self.inventory:
			raise GameError("%s already in game inventory" % str(item))
		self.inventory.append(item)
		
		if item.xmlnode.hasAttribute("name"):
			names = item.xmlnode.getAttribute("name").split(",")
			name = lib.Noun(*names)
			
			item.noun = name
			name.item = item
			
		if item.xmlnode.hasAttribute("adjective"):
			names = item.xmlnode.getAttribute("adjective").split(",")
			name = lib.Adjective(*names)
			
			item.noun.adjective = name
			
		self.lib.add(item.noun)

	def removeItem(self, item):
		self.inventory.remove(item)
		self.lib.remove(item.noun)
		item.noun.item = None
		
	def writeIntro(self, output):
		output.writeRaw(self.introduction)
		
	@property
	def state(self):
		return self._states[-1]
		
	@property
	def prompt(self):
		return self.state.prompt
		
	def newState(self, value):
		value.addEventListener(states.SWITCH, self.onStateChange)
		value.addEventListener(states.KILL, self.onStateKill)
		self._states.append(value)
		
	def onStateChange(self, event):
		self.newState(event.state)
		
	def onStateKill(self, event):
		if event.target != self._states[-1]:
			raise StateError("Topmost state expected")
			
		self._states.pop()
		
	def getLib(self):
		return io.lib.defaults.defaultLibrary()
		
	def parse(self, s):
		return self.lib.parse(s)
		
	def handle(self, input):
		return self.state.handle(input)
		
	def input(self, s):
		return self.handle(self.parse(s))

	def find(self, name):
		for item in self.inventory:
			if item.name == name:
				return item
		
	def buildFromXML(self, doc, main):
		context = nodes.Context(
			default=DefaultContext(self, main)
		)
		
		context.getNSFromXML(doc.documentElement)
		tree = nodes.ContextTree(context)
		
		for item in tree.getTree(doc.documentElement):
			if isinstance(item, Item):
				self.addItem(item)
				
	def getContext(self):
		return Context(game=self)
		
		
class DefaultContext(object):
	def __init__(self, game, main):
		self.main = main
		self.game = lambda x: game
		self.meta = XMLMeta
		

class XMLMeta(nodes.XMLINode):
	def __init__(self, xmlnode):
		nodes.XMLINode.__init__(self, xmlnode)
		self.shouldTraverse = False
		
	def assignParent(self, parent):
		for child in self.xmlnode.childNodes:
			if child.nodeType != 1: #	not element
				continue
				
			if child.localName == "title":
				parent.title = self.getChildString(child)
			elif child.localName == "description":
				parent.description = self.getChildString(child)
			elif child.localName == "version":
				parent.version = self.getChildString(child)
			elif child.localName == "introduction":
				parent.introduction = self.getChildString(child)

