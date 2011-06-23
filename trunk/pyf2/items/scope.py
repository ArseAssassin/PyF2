class Scope(object):
	def __init__(self, base):
		self.base = base
		
	def topDown(self):
		topmost = self.getTopmost()
		l = self.getChildren(topmost)
		return [topmost] + l
		
	def travelUp(self):
		l = []
		
		current = self.base
		
		while current.owner != None:
			l.append(current)
			current = current.owner
			
		for x in reversed(l):
			yield x
		
		
	def getTopmost(self, item=None):
		if not item:
			item = self.base
			
		if item.owner.owner == None:
			return item
		else:
			return self.getTopmost(item.owner)
		
	def getChildren(self, item=None):
		if not item:
			item = self.base
			
		l = []
			
		for child in item.children:
			l.append(child)
			l.extend(self.getChildren(child))
			
		return l
		
	def __iter__(self):
		for x in self.getChildren():
			yield x
			
	def __contains__(self, other):
		return other in self.topDown()
	