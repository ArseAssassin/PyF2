import unittest

from lib import *
from defaults import defaultLibrary

class TestSuite(unittest.TestCase):
	
	def setUp(self):
		self.word = Word("blah")
		self.noun = Noun('bleh')
		self.assault = Attack('assault', 'attack')
		self.verb = Verb('turn off', 'close')
		self.egg = Noun("egg")
		self.lib = defaultLibrary()
		pick = Noun("pick axe", 'pick', 'axe')
		pick.adjective = Adjective("rusty", "metal")
		rock = Noun("boulder", 'rock', 'stone')
		rock.adjective = Adjective("gray", "hard", "cold")
		self.lib.add(rock)
		self.lib.add(self.egg)
		self.lib.add(pick)
		
		self.lib.add(Noun("plant pot"))
		self.lib.add(Noun("plant"))
		self.lib.add(Verb("plant"))
		
	def test_wildcards(self):
		self.assertEqual(self.word.wildcards, set(['*']))
		self.assertEqual(self.noun.wildcards, set(['*', '*noun']))
		
	def test_names(self):
		self.assertEqual(self.word.name, "blah")
		self.assertEqual(self.noun.name, "bleh")

	def test_nameLists(self):
		self.assertEqual(self.word.names, set(['*', 'blah']))
		self.assertEqual(self.noun.names, set(['*', '*noun', "bleh"]))
		self.assertEqual(self.assault.names, set(['*', '*verb', '*attack', "assault", 'attack', '*touch']))
		
	def test_articles(self):
		self.assertTrue(self.noun.indefinite == "a bleh")
		self.assertTrue(self.egg.indefinite == "an egg")
		
	def test_stringTokenization(self):
		s = 'assault the man'.split()
		f = self.assault.getStringTokens(s)[0]
		self.assertEqual(f.start,0)
		self.assertEqual(f.end,1)
		self.assertEqual(f.value,1)

		s = 'say bleh to the duck'.split()
		f = self.noun.getStringTokens(s)[0]
		self.assertEqual(f.start,1)
		self.assertEqual(f.end, 2)
		self.assertEqual(f.value,1)

		s = 'turn off glenn close'.split()
		f = self.verb.getStringTokens(s)[0]
		self.assertEqual(f.start, 0)
		self.assertEqual(f.end,2)
		self.assertEqual(f.value,2)
		
	def test_libTokenization(self):
		s = 'travel west with horse'
		self.assertEqual(len(self.lib.tokenize(s.split())), 3)

	def test_mutability(self):
		self.egg.add('temporary')
		self.assertTrue('temporary' in self.egg._names)
		self.egg.remove('temporary')
		self.assertTrue('temporary' not in self.egg._names)

	def test_wordMatching(self):
		self.assertEqual(self.assault, "*verb")
		self.assertEqual(self.assault, "attack")
		self.assertEqual(self.assault, "assault")
		self.assertEqual(self.noun, "bleh")
		self.assertEqual(self.noun, "*noun")
		self.assertEqual(self.word, "*")

		self.assertEqual(self.word, self.word)
		self.assertEqual(self.word, Unknown('blah', 'bleh'))
		self.assertEqual(self.assault, Unknown('attack'))
		self.assertEqual(self.assault, Unknown('bimboo', 'assault'))
		self.assertEqual(self.assault, '*touch')
		self.assertEqual(Unknown("wand"), Unknown('wand'))
		
	def test_normalization(self):
		self.assertEqual(self.lib.normalize([None]*5), [None])

	def test_sentenceMatching(self):
		s = self.lib.parse("get book")
		self.assertEqual(s, 'take book')

		s = self.lib.parse("x egg")
		self.assertNotEqual(s, 'examine')

		s = self.lib.parse("unknown command")
		self.assertEqual(s, ('unknown', 'command'))
		
		s = self.lib.parse('take wand')
		self.assertEqual(s, 'take wand')
		
		self.assertEqual(s, ("take", "wand"))

		s = self.lib.parse('hit rock using pick axe')
		
		self.assertEqual(s, 'punch gray stone with pick')
		self.assertEqual(s, 'punch stone with pick')
		self.assertEqual(s, 'punch rock with axe')
		
		self.assertNotEqual(s[1], s[3])
		
		self.assertEqual(s.noun, 'rock')
		
		self.assertEqual(s[1:], 'rock with pick')
		
	def test_disambiguation(self):
		self.assertRaises(DisambiguationError, 
			lambda: self.lib.parse("plant the plant in the plant pot")
		)


if __name__ == "__main__":
	unittest.main()