# encoding: utf-8

START_CODE_TOKEN = "{{"
END_CODE_TOKEN = "}}"

class Context(object):
	def __init__(self, **kwargs):
		self.d = kwargs
		
	def put(self, name, value):
		self.d[name] = value
		
	def getContext(self):
		d = self.d.copy()
		d["START_CODE"] = START_CODE_TOKEN
		d["END_CODE"] = END_CODE_TOKEN
		
		return d
		
	def tokenize(self, s):
		stack = TokenList()
		
		global b 
		b = ""
		
		def flushBuffer(cutTail=False):
			global b
			s = b
			if cutTail:
				s = s[:-2]
			if not stack.current:
				stack.append(StringToken())
				
			stack.current.write(s)
			b = ""
		
		i = 0
		while i < len(s):
			b += s[i]
			
			if b.endswith(START_CODE_TOKEN):
				flushBuffer(True)
				stack.append(CodeToken())
			elif b.endswith(END_CODE_TOKEN):
				flushBuffer(True)
				stack.append(StringToken())
			
			i += 1
			
				
		flushBuffer(False)
			
				
		return stack
		
	def evaluate(self, s):
		tokenList = self.tokenize(s)
		self.context = self.getContext()

		return tokenList.evaluate(self.context)

class Token(object):
	def __init__(self):
		self.source = ""
		self.closed = False
		
	def close(self):
		self.closed = True
		
	def write(self, s):
		if self.closed:
			raise Exception("Buffer already closed")
		self.source += s
		
	@property
	def code(self):
		return self.source
		

class TokenList(Token):
	def __init__(self):
		self.list = []
		
	@property
	def current(self):
		try:
			return self.list[-1]
		except IndexError:
			return None
		
	def append(self, token):
		self.list.append(token)
			
	def __len__(self):
		return len(self.list)
		
	def __getitem__(self, i):
		return self.list[i]
			
	def evaluate(self, context):
		l = filter(lambda x: x.code != "", self.list)
		
		if len(l) == 1 and type(l[0]) == CodeToken:
			return l[0](context)
		
		output = u''.join([unicode(token(context)) for token in l])
			
		return output
		
	def __repr__(self):
		return "<TokenList [%s]>" % ', '.join([token.__repr__() for token in self.list])


class StringToken(Token):
	def __call__(self, context):
		return self.code
		
	def __repr__(self):
		return "<StringToken %s>" % self.code
		
		
class CodeToken(Token):
	def __call__(self, context):
		return eval(self.code.strip(), context)
		
	def __repr__(self):
		return "<CodeToken %s>" % self.code.strip()
		
	@property
	def code(self):
		return self.source.strip()


