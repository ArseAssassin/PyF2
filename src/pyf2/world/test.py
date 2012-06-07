from xmlinit.test import *

from mock import Mock

from scope import Scope
from base import Message, Property
from items import Item
from events import game_events
from errors import *
import props

import unittest

class test_scope(unittest.TestCase):
	def setUp(self):
		self.tree = makeTestNodeTree()
		self.scope = Scope(b.instances[0])
		
	def test_locating(self):
		self.assertEqual(self.scope.getTopmost(), b.instances[0])
		self.assertEqual(self.scope.getChildren(), 
			[c.instances[0], d.instances[0], c.instances[1]])
		# self.assertEqual(self.scope.topDown(), 
		# 	[c.instances[0], d.instances[0], c.instances[1]])
			
	def test_iterating(self):
		l = []
		for x in self.scope:
			l.append(x)
			
		self.assertEqual(l, [c.instances[0], d.instances[0], c.instances[1]])
		
		for x in self.scope:
			self.assertTrue(x in self.scope)
			
		

class test_Message(unittest.TestCase):
	def setUp(self):
		class testItem(object):
			var = Message('test', True)
			var2 = Message("nope", True)
			var3 = Message("dope", "rope")
			var4 = Message("hope", "cope")
			
			def getXMLAttribute(self, name):
				if name == 'test':
					return 'stuff'
				
				return None
				
		self.testItem = testItem()
		
	def test_getting(self):
		self.assertEqual(self.testItem.var, "stuff")
		self.assertEqual(self.testItem.var2, True)
		
	def test_setting(self):
		self.assertEqual(self.testItem.var3, "rope")
		self.assertEqual(self.testItem.var4, "cope")

		self.testItem.var3 = False
		self.testItem.var4 = "dude"
		
		self.assertEqual(self.testItem.var3, False)
		self.assertEqual(self.testItem.var4, "dude")


class test_Item(unittest.TestCase):
	def setUp(self):
		def f(event):
			self.moveHandler.l.append(1)
			
		self.moveHandler = Mock(side_effect=f)
		self.moveHandler.l = []
		
		self.item = Item()
		self.item.noun = "item"
		self.destination = Item()
		self.destination.noun = "destination"
		
	def test_movement(self):
		self.item.addEventListener(game_events.MOVE, self.moveHandler)
		self.destination.addEventListener(game_events.ACQUIRE, self.moveHandler)
		
		self.item.move(self.destination)
		self.assertRaises(MoveError, lambda: self.destination.move(self.item))
		
		self.assertEqual(self.moveHandler.l, [1, 1])
		self.assertEqual(self.item.owner, self.destination)
		self.assertEqual(self.destination.inventory, [self.item])
		
		self.item.move(None)

		self.assertEqual(self.moveHandler.l, [1, 1, 1])
		self.assertEqual(self.item.owner, None)
		self.assertEqual(self.destination.inventory, [])

	def test_childAccess(self):
		self.item.move(self.destination)
		self.assertTrue(self.destination.has(self.item))
		self.assertEqual(self.destination.get(self.item), self.item)
		self.assertEqual(self.destination.get(self.item), "item")
		
	def test_comparison(self):
		self.assertEqual(self.item, "item")
		self.assertEqual(self.destination, "destination")
		
	def getMockProp(self):
		mockProp = Mock(spec=Property)
		mockProp._handle = Mock()
		return mockProp
		
	def test_props(self):
		self.item.addProp(self.getMockProp())
		self.item.addProp(self.getMockProp())
		self.item.addProp(self.getMockProp())
		self.assertEqual(len(self.item.props), 3)
		
		i, o = Mock(), Mock()
		
		self.item.owner = Mock()
		self.item._handle(i, o)
		self.item.owner = None
		
		for prop in self.item.props:
			prop._handle.assert_called_once_with(i, o)
			
		self.item.removeProp(self.item.props[0])
		self.assertEqual(len(self.item.props), 2)
		
		while self.item.props:
			self.item.props.pop()
			
	def test_propertyAccess(self):
		self.item.addProp(Property())
		self.assertNotEqual(self.item.props.Property, None)
		
		
class test_xml(unittest.TestCase):
	def setUp(self):
		self.item = Item()
		
		xml = "<Item />"
		node = minidom.parseString(xml).firstChild
		
		self.item.initXML(node)

		
class test_props(unittest.TestCase):
	def setUp(self):
		self.prop = props.Describable()
		
		xml = "<Describable>hello</Describable>"
		node = minidom.parseString(xml).firstChild
		
		self.prop.initXML(node)

		self.prop2 = props.Describable()
		
		xml = "<Describable>{{True}}</Describable>"
		node = minidom.parseString(xml).firstChild
		
		self.prop2.initXML(node)
		
	def test_variables(self):
		self.assertEqual(self.prop.description, "hello")
		
	def test_handling(self):
		i = ("examine", "*self")
		o = Mock()
		o.write = Mock()
		self.prop._handle(i, o)
		
		o.write.assert_called_once_with("hello")
		
		o.write.reset_mock()
		self.prop2._handle(i, o)
		
		o.write.assert_called_once_with("{{True}}")
		

if __name__ == '__main__':
	unittest.main()