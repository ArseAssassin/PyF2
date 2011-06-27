from lib import *
from lib.test import *

from context import *
from output import *

import unittest, mock
from mock import Mock

class test_Context(unittest.TestCase):
	def setUp(self):
		class mockInput:
			verbs = []
			nouns = []
			verb = None
			noun = None
			
		self.context = Context()
		
		self.sampleContext = {
			"two": 2,
			"true": True,
			"name": "PyF"
		}
		
	def test_tokenization(self):
		tokens = self.context.tokenize("You drop {{input.noun.definite}} on the ground.")
		self.assertEquals(self.context.tokenize("test {{test }} yep")[1].code, "test")
		
		self.assertEquals(tokens[1].code, "input.noun.definite")
		self.assertEquals(len(tokens), 3)

		self.assertEquals(len(self.context.tokenize("hello {{ what is this }} yep")), 3)
		# self.assertEquals(len(self.context.tokenize("hello {{ what '{{' is '}}' this }} {{ yeah }} yep")), 4)
		self.assertEquals(len(self.context.tokenize("test {{test}} yep")), 3)
		self.assertEquals(len(self.context.tokenize("test {{test }} yep")), 3)
		self.assertEquals(len(self.context.tokenize("test {{ test}} yep")), 3)
		self.assertEquals(len(self.context.tokenize("test {{ test}}.")), 3)
		self.assertEquals(len(self.context.tokenize("test {{test my stuff}} yep")), 3)
		
		
		
	def test_evaluation(self):
		c = CodeToken()
		c.write("True")
		self.assertEquals(c(None), True)

		c = CodeToken()
		c.write("two")
		self.assertEquals(c(self.sampleContext), 2)
		
		l = TokenList()
		c = CodeToken()
		c.write("two")
		l.append(c)

		c = StringToken()
		c.write(" what is this")
		l.append(c)
		
		self.assertEquals(l.evaluate(self.sampleContext), u"2 what is this")
		
	def test_contextBuilding(self):
		self.assertEquals(
			self.context.evaluate("{{ True }}"),
			True
		)


class test_Output(unittest.TestCase):
	def setUp(self):
		c = mock.Mock(spec=Context)
		c.evaluate = lambda x: x
		
		self.output = Output(c)
		self.plainOutput = Output()
		
	def test_output(self):
		self.output.write("hello", -1)
		self.assertRaises(
			OutputClosed, lambda: self.output.write("world")
		)
		self.assertEquals(self.output.text, "hello\nworld")
		
		self.assertRaises(
			OutputClosed, lambda: self.plainOutput.write("world")
		)
		
		self.output.clean()
		
		self.output.write("hello", -1)
		self.output.write("world", -1)
		try:
			self.output.close()
		except OutputClosed, e:
			self.assertEquals(self.output.text, "hello\nworld")
		
		
if __name__ == "__main__":
	unittest.main()
    
if __name__ == '__main__':
	unittest.main()