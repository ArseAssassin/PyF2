from world.xmlinit import nodes
from world import Item, Actor
from states import Controlled

def buildGameFromXML(doc, main):
	context = nodes.Context(
		default=DefaultContext(main)
	)
	
	context.getNSFromXML(doc.documentElement)
	tree = nodes.ContextTree(context)
	
	game = None
	
	for item in tree.getTree(doc.documentElement):
		if not game: #	game will always be the first node
			game = item
			continue
			
		if isinstance(item, Item):
			if isinstance(item, Actor):
				game.newState(Controlled(item))
			game.addItem(item)
			
	return game
		
		
class DefaultContext(object):
	def __init__(self, main):
		self.main = main
		self.meta = XMLMeta
		
	def __getattr__(self, name):
		return getattr(self.main, name)
		

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

