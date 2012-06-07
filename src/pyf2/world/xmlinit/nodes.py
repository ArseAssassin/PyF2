from errors import NamespaceError, ParentError

import pdb

from xml.dom import minidom

def getModule(s):
	m = __import__(s)
	for name in s.split(".")[1:]:
		m = getattr(m, name)
		
	return m

	
class XMLINode(object):
	i = None
	
	def __init__(self, xmlnode):
		self.xmlnode = xmlnode
		self.owner = None
		
		self.shouldTraverse = True
		
		if not hasattr(self, 'children'):
			try:
				self.children = []
			except AttributeError:
				pass
		if not self.i:
			self.__class__.i = self
			
		self.initFromXML()
		
	def initFromXML(self):
		pass
		
	def getXMLAttribute(self, name):
		return self.xmlnode.getAttribute(name)
		
	def assignParent(self, parent):
		if self.owner != None:
			raise ParentError()
		self.owner = parent
		self.owner.children.append(self)
		
	def getChildString(self, node=None):
		if not node:
			node = self.xmlnode
			
		s = ""
		for x in node.childNodes:
			if x.nodeType == 3:
				s += x.wholeText
				
		return s.strip()

	@property
	def data(self):
		return self.getChildString()
	
		
class Context(object):
	def __init__(self, **namespaces):
		self.namespaces = namespaces
		self.default = []
		if 'default' in self.namespaces:
			self.default.append(self.namespaces['default'])
			del self.namespaces['default']
		
	def add(self, ns):
		self.namespaces.append(ns)
		
	def acquire(self, name, ns=None):
		if ns:
			try:
				return getattr(self.namespaces[ns], name)
			except AttributeError:
				pass
		else:
			for x in self.default:
				if getattr(x, name, None):
					return getattr(x, name)
				
		raise NamespaceError("Name %s not found in namespace %s" % (name, ns))
			
			
	def addDefaults(self, namespace):
		pass
			
		
	def getNSFromXML(self, node):
		for a in node.attributes.values():
			if a.prefix == "xmlns":
				self.namespaces[a.localName] = getModule(a.value)
		

class ContextTree(object):
	def __init__(self, context):
		self.context = context
		
	def getTree(self, xmlnode):
		xmlinode = self.context.acquire(xmlnode.localName, xmlnode.prefix)(xmlnode)
		all = [xmlinode]
		
		if xmlinode.shouldTraverse:
			for child in xmlnode.childNodes:
				if child.nodeType != 1:
					continue
				
				for x in self.getTree(child):
					try:
						x.assignParent(xmlinode)
					except ParentError:
						pass
					all.append(x)
			
		return all
			
			
		