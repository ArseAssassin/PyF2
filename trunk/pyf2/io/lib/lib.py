import weakref

from errors import *

CONSONANTS = "b,c,d,f,g,h,j,k,l,m,n,o,p,q,r,s,t,v,w,x,z,uni,yo,yu,ya,yi".split(",")

class Lib(object):
	def __init__(self, *list):
		self.words = set()
		for word in list:
			self.words.add(word)
			
	def add(self, *words):
		self.words.update(words)
		
	def __contains__(self, other):
		return other in self.words
		
	def tryDisambiguate(self, options):
		return options
		
	def parse(self, s):
		words = s.split()
		tokens = self.tokenize(words)
		
		l = [None for x in words]
		
		for x in tokens:
			similar = filter(lambda y: x == y, tokens)
			similar = self.tryDisambiguate(similar)
			
			if len(similar) > 1:
				raise DisambiguationError("Can't disambiguate between words [%s]" % [x.__repr__() for x in similar],
					s, similar)
		
		for token in tokens:
			if filter(None, l[token.start:token.end]) == []: # find whether parts of sentence are still available
				for i in range(token.start, token.end): # link parts to words
					l[i] = token.word
		
		l = self.coverUnrecognized(l, words)
		l = self.normalize(l)		
				
		
		l = filter(lambda x: not x.ignore, l)
				
		return Sentence(l, self, )
				
				
	def coverUnrecognized(self, l, words):
		for i in xrange(len(l)):
			if l[i] is None:
				l[i] = Unknown(words[i])
				
		return l
		
	def normalize(self, l):
		for i in reversed(xrange(len(l))):
			if i == 0:
				break
			elif l[i-1] is l[i]:
				del l[i]
				
		return l
		
		
	def tokenize(self, s):
		tokens = []
		for word in self.words:
			try:
				tokens.extend(word.getStringTokens(s))
			except IndexError:
				pass
				
		tokens.sort(key=lambda x:(-x.value, x.start))
		
		return tokens

class Word(object):
	ignore = False
	
	def __init__(self, *names):
		names = [name.strip() for name in names]
		self.name = names[0]
		self._names = set(names)
		
	def add(self, name):
		self._names.add(name)
		
	def remove(self, name):
		self._names.remove(name)
		
	@property
	def names(self):
		s = set()
		s.update(self._names)
		s.update(self.wildcards)
		return s
	
	@property
	def wildcards(self):
		def recurse(r):
			if r in (Word, object):
				return set()
			l = set(["*%s" % r.__name__.lower()])
			for x in r.mro(): # mro = method resolution order
				if x == r:
					continue
				l.update(recurse(x))
				
			return l
			
		l = set(["*"])
		l.update(recurse(type(self)))
		return l
		
	def __eq__(self, other):
		if isinstance(other, type(None)):
			return False
		elif isinstance(other, basestring):
			for word in self.names:
				if word == other:
					return True
		else:
			othernames = other._names
			for word in self._names:
				for otherword in othernames:
					if otherword == word:
						return True

		return False
		
	def __ne__(self, other):
		return self.__eq__(other) == False
		
	def __contains__(self, other):
		return other in self.names
	
	def __iter__(self):
		return iter(self.names)
		
	def getStringTokens(self, s):
		tokens = []
		for i in xrange(len(s)):
			w = s[i]
			for name in self.names:
				parts = name.split()
				try:
					for x in xrange(len(parts)):
						name = parts[x]
						if s[i+x] != name: # doesn't match name
							raise MatchingError
					tokens.append(MatchToken(self, name, i, i+len(parts)))
					
				except MatchingError:
					pass
						
		return tokens
					
	def __repr__(self):
		return '<%s "%s">' % (self.__class__.__name__, self.name)
			
class Noun(Word):
	def __init__(self, *words):
		Word.__init__(self, *words)
		self.adjective = None
		
	@property
	def item(self):
		return self._item()
		
	@item.setter
	def item(self, value):
		self._item = weakref.ref(value)
	
	@property
	def definite(self):
		return 'the %s' % self.name
	
	@property
	def indefinite(self):
		for f in CONSONANTS:
			if self.name.startswith(f):
				return 'a %s' % self.name
				
		return 'an %s' % self.name
		
	def getStringTokens(self, s):
		tokens = Word.getStringTokens(self, s)
		if self.adjective:
			a = self.adjective.getStringTokens(s)
			for x in a:
				for y in tokens:
					if x.end == y.start:
						y.mergeTo(x)
						
		return tokens
		
		
class Adjective(Word):
	ignore = True
		
class Article(Word):
	ignore = True
	
class Direction(Word):
	pass
	
class Preposition(Word):
	pass

class Verb(Word):
	pass
	
class Touch(Verb):
	pass
	
class Attack(Touch):
	pass

class Question(Word):
	pass

class Unknown(Word):
	pass
	
class MatchToken(object):
	'''Abstraction for a possible match inside a sentence.'''
	
	def __init__(self, word, string, start, end):
		self.start = start
		self.end = end
		self.word = word
		self.string = string
		
	def __len__(self):
		return self.end-self.start
		
	@property
	def value(self):
		return self.end-self.start
		
	def intersects(self, other):
		for x in (self.start, self.end):
			if x > other.start and x < other.end:
				return True
				
		return False
		
	def mergeTo(self, other):
		self.start = min(self.start, other.start)
		self.end = max(self.end, other.end)
		
	def __repr__(self):
		return "<Match token start=%i end=%i value=%i>" % (self.start, self.end, self.value)
		
	def __eq__(self, other):
		return (self.start == other.start and self.end == other.end)
			

class Sentence(object):
	def __init__(self, words, lib=Lib(), originalInput=None):
		self.actor = None
		self.words = words
		self.lib = lib
		self.originalInput = originalInput
		
	def __getslice__(self, start, end):
		return Sentence(self.words[start:end], self.lib)
	
	def __contains__(self, other):
		return other in self.words
		
	def __eq__(self, other):
		if isinstance(other, basestring):
			return self == self.lib.parse(other)
			
		if len(other) != len(self):
			return False
			
		for i in xrange(len(other)):
			if other[i] != self[i]:
				return False
				
		return True
		
	def __len__(self):
		return len(self.words)
		
	def __getitem__(self, i):
		return self.words[i]
		
	def __repr__(self):
		return '<Sentence "%s">' % (' '.join([x.name for x in self.words]))
		
	@property
	def nouns(self):
		return filter(lambda x: x == "*noun", self)
				
	@property
	def noun(self):
		return self.nouns[0]
			
	@property
	def verbs(self):
		return filter(lambda x: x == "*verb", self)
			
	@property
	def verb(self):
		return self.verbs[0]
			
	@property
	def items(self):
		return map(lambda x:x.item, filter(lambda x: x == "*noun", self))
			
	@property
	def item(self):
		return self.items[0]
			
		