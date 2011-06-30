import unittest
from events import *
import game_events

class TestEvent(Event):
	def __init__(self, type="", **kwargs):
		self.data = kwargs
		self.type = type
		
		
class Node(EventDispatcher):
	TOUCHED = Event("touch")
	NEW_TOUCHED = Event("new_touched")
	
	def __init__(self, name):
		EventDispatcher.__init__(self)
		self.flag = False
		self.owner = None
		self.name = name
		
	def addChild(self, child):
		child.owner = self
		
	def touched(self, event):
		self.flag = (self.flag == False)


def makeTestNodeTree():
	a = Node('a')
	b = Node('b')
	a.addChild(b)

	c, d = Node('c'), Node('d')

	b.addChild(c)
	b.addChild(d)
	
	return a, b, c, d
		
class test_Event(unittest.TestCase):
	def setUp(self):

		self.a, self.b, self.c, self.d = makeTestNodeTree()


	def test_eventPropagation(self):
		a, b, c, d = self.a, self.b, self.c, self.d
		
		d.addEventListener(Node.TOUCHED, d.touched)
		d.dispatchEvent(Node.TOUCHED())

		self.assertTrue(d.flag)

		a.addEventListener(Node.TOUCHED, a.touched)
		b.addEventListener(Node.TOUCHED, b.touched)

		d.dispatchEvent(Node.TOUCHED())

		self.assertTrue(a.flag)
		self.assertTrue(b.flag)
		self.assertFalse(d.flag)
		
		c.addEventListener(Node.NEW_TOUCHED, c.touched)

		c.dispatchEvent(Node.NEW_TOUCHED())

		self.assertTrue(a.flag)
		self.assertTrue(b.flag)
		self.assertTrue(c.flag)
		self.assertFalse(d.flag)
		
	def test_eventListeners(self):
		self.d.addEventListener(Node.TOUCHED, None)
		self.assertEqual(len(self.d.listeners[Node.TOUCHED.type]), 1)
		self.d.removeEventListener(Node.TOUCHED, None)
		self.assertEqual(len(self.d.listeners[Node.TOUCHED.type]), 0)



if __name__ == '__main__':
	unittest.main()