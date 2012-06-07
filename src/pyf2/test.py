from mock import Mock

from xml.dom import minidom

import world.items
import world.scope
import game
import states
import init
from errors import StateError

from io.output import OutputClosed

#	import all unit test
from world.test import *
from io.test import *

import unittest


def testHandle(input, output):
	if input == "look":
		output.write("looking", 1)
		output.write("away", 0)
	elif input == "get book":
		output.write("got it")
	else:
		output.write("hello")

def mockActor():
	actor = Mock()
	actor._handle = Mock(side_effect = testHandle)
	
	scope = Mock(spec=world.scope.Scope)
	scope.topDown = lambda: [actor]
	
	actor.getScope = lambda: scope

	return actor


class test_State(unittest.TestCase):
	def setUp(self):
		self.actor = mockActor()
		self.scope = self.actor.getScope()
		
		self.controlled = states.Controlled(self.actor)
		
	def test_stateHandling(self):
		self.assertEqual(self.scope.topDown(), [self.actor])
		self.assertEqual(self.controlled.getScope(), self.scope)
		self.assertEqual(self.controlled.getScopedItems(), [self.actor])
		
		def f(a):
			raise OutputClosed()
		
		output = Mock()
		output.write = Mock(side_effect=f)
		
		self.assertRaises(OutputClosed, lambda: self.actor._handle(output, output))
		output.write.assert_called_once_with("hello")
		
		for x in self.controlled.getScopedItems():
			self.assertRaises(OutputClosed, lambda: x._handle(output, output))
		
		input = Mock()
		input.nouns = []
		input.items = []
		output = self.controlled.handle(input)
		
		self.assertEqual(output.text, "hello")
			

class test_GameInput(unittest.TestCase):
	def setUp(self):
		self.game = game.Game()
		self.state1 = states.State()
		self.state2 = states.State()
		self.game.newState(self.state1)
		
	def test_stateSwitching(self):
		self.state1.switch(self.state2)
		self.assertEqual(self.game.state, self.state2)
		self.assertRaises(StateError, lambda: self.state1.kill())
		self.state2.kill()
		self.assertEqual(self.game.state, self.state1)
		
	def test_gameHandling(self):
		actor = mockActor()
		controlled = states.Controlled(actor)
		self.game.newState(controlled)
		
		input = self.game.parse('look')
		output = self.game.handle(input)
		
		self.assertEqual(output.text, "looking\naway")

		input = self.game.parse('get book')
		
		output = self.game.handle(input)
		
		self.assertEqual(output.text, "got it")
		
	def test_intro(self):
		output = Mock()
		output.writeRaw = Mock()
		
		self.game.writeIntro(output)
		output.writeRaw.assert_called_once_with("undefined")
		
		
class test_GameInitiation(unittest.TestCase):
	def setUp(self):
		self.game = game.Game()
		
		self.items = [Item() for x in range(4)]
		
		xml = '''
			<root>
				<Item name="item1" adjective="ugly" />
				<Item name="item2,thing" adjective="sharp,useful" />
				<Item name="item3" />
				<Item name="item4" />
			</root>
		'''
		i = 0
		
		for node in minidom.parseString(xml).getElementsByTagName("Item"):
			self.items[i].initXML(node)
			self.game.addItem(self.items[i])
			
			i += 1
	
	def test_nameAssignments(self):
		self.assertEqual(len(self.items), 4)
		self.assertEqual(self.items[0].noun, "item1")
		self.assertTrue(self.items[0].noun in self.game.lib)
		
		self.assertEqual(self.items[1].noun.adjective, "sharp")
		
		self.assertEqual(self.game.parse("sharp thing"), "useful item2")
		
	
		
class test_GameIntegration(unittest.TestCase):
	def setUp(self):
		xml = '''
		<g:Game xmlns:g="game" xmlns:i="world.items" xmlns:p="world.props">
			<meta>
				<title>Test game</title>
				<description>Test description</description>
				<version>1.0</version>
				<author>Test</author>
			</meta>
		
			<i:Item name="room">
				<p:Room>room1</p:Room>

				<i:Item name="yourself" id="initial_actor">
					<p:Describable>As handsome as ever.</p:Describable>
					<i:Item name="cloak">
						<p:Portable droppable="{{True}}" />
					</i:Item>
				</i:Item>
				<p:Traversable>
					<east>room2</east>
				</p:Traversable>
			</i:Item>

			<i:Item name="room2">
				<i:Item name="table">
					<p:Describable description="Sturdy table." />
					<p:Surface />
				</i:Item>

				<p:Traversable>
					<west>room</west>
				</p:Traversable>
				<p:Room>room2</p:Room>
			</i:Item>
		</g:Game>
		'''

		doc = minidom.parseString(xml)

		self.complexGame = init.buildGameFromXML(doc, None)
		
		self.room1 = self.complexGame.find("room")
		self.room2 = self.complexGame.find("room2")
		self.player = self.complexGame.find("initial_actor")
		self.cloak = self.complexGame.find("cloak")
		self.table = self.complexGame.find("table")
		
	def assertInput(self, input, output):
		if not isinstance(output, basestring):
			output = "\n".join(output)
			
		self.assertEqual(self.cg.input(input).text, output)
		
	@property
	def cg(self):
		return self.complexGame
		
	def test_metaDefinitions(self):
		self.assertEqual(self.cg.title, "Test game")
		self.assertEqual(self.cg.description, "Test description")
		self.assertEqual(self.cg.version, "1.0")
		self.assertEqual(self.cg.author, "Test")
			
	def test_gameStructure(self):
		self.assertEqual(self.player.owner, self.complexGame.find("room"))
		self.assertEqual(self.complexGame.find('table').owner, self.complexGame.find("room2"))

		scope = self.player.getScope()
		
		self.assertTrue(self.complexGame.inventory[0].has('initial_actor'))
		
		self.assertNotEqual(self.complexGame.inventory[1].props.Describable, None)
		self.assertEqual(self.complexGame.inventory[1].props.Describable.description, "As handsome as ever.")
		
		self.assertTrue(self.complexGame.find('room').props.Traversable != None)
		
	def test_handling(self):
		
		o = Mock()
		o.write = Mock()
		# i = (self.complexGame.find('room').props.Traversable.dir,)
		# self.assertRaises(AttributeError, lambda: self.complexGame.find("room")._handle(i, o))
		## 			not sure what this tests
		
	def test_gameInput(self):
		input = self.complexGame.parse('east')
		self.assertEqual(input, ("*direction",))
		self.assertEqual(input, "east")
		output = self.complexGame.handle(input)
		self.assertEqual(output.text, "room2\nroom2")
		
		input = self.complexGame.parse("drop cloak")
		self.assertEqual(input, "drop cloak")
		self.assertEqual(input.noun, self.complexGame.find("cloak").noun)
		
		self.assertEqual(self.complexGame.input("drop cloak").text, "You drop the cloak on the ground.")
		self.assertEqual(self.cloak.owner, self.room2)
		
		self.assertEqual(self.cg.input("examine").text, "\n".join([self.player.owner.name, self.player.owner.name, "You can also see %s here." % self.cloak.noun.indefinite]))

		self.assertInput("put cloak on table", "You place %s on %s." % (self.cloak.definite, self.table.definite))
		
		
if __name__ == '__main__':
	unittest.main()