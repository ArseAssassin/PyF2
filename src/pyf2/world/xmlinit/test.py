import unittest
from xml.dom import minidom

from nodes import *
import sys

class Node(XMLINode):
	instances = []
	def __init__(self, *l):
		XMLINode.__init__(self, *l)
		self.instances.append(self)


class NamedNode(Node):
	@property
	def name(self):
		return self.xmlnode.localName
		
		

class a(NamedNode):
	instances = []

	
class b(NamedNode):
	instances = []

	
class c(NamedNode):
	instances = []

	
class d(NamedNode):
	instances = []
	

def makeTestNodeTree():
	xml = '''
	<a>
		<b>
			<c>
				bleh
			</c>
			<d>
				blah
			</d>
			<c />
		</b>
		
		<b>
			<d />
		</b>
	</a>
	'''
	
	context = Context(
		default=sys.modules[__name__]
	)
	
	doc = minidom.parseString(xml)
	doc.normalize()

	context.getNSFromXML(doc.documentElement)
	
	tree = ContextTree(context)
	
	return tree.getTree(doc.documentElement)


class TestSuite(unittest.TestCase):
	def setUp(self):
		self.nodes = makeTestNodeTree()
		
	def test_treeBuilding(self):
		self.assertEqual(len(self.nodes), 7)
		self.assertEqual(type(b.instances[1].owner), a)
		self.assertEqual(type(c.instances[0].owner), b)
		
	def test_treeChildren(self):
		self.assertEqual(len(a.instances[0].children), 2)
		self.assertEqual(len(c.instances[0].children), 0)
		# self.assertEqual(a.instances[0].children, b.instances)
	
	def test_data(self):
		self.assertEqual(c.instances[0].data, "bleh")
		self.assertEqual(d.instances[0].data, "blah")
		self.assertEqual(d.instances[1].data, "")
	
		

if __name__ == "__main__":
	unittest.main()