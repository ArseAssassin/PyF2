'''Generic event handling based on DOM level 2 event model.'''

CAPTURING_PHASE = "capturingPhase"
AT_TARGET = "atTarget"
BUBBLING_PHASE = "bubblingPhase"

class EventDispatcher(object):
	def __init__(self):
		self.listeners = {}
		if not hasattr(self, 'owner'):
			self.owner = None
		
	def dispatchEvent(self, event):
		event.target = self
		
		tree = self.getTree()
		
		event.phase = CAPTURING_PHASE
		
		for x in tree:
			x.handleEvent(event)
			
		event.phase = AT_TARGET
		self.handleEvent(event)
			
		event.phase = BUBBLING_PHASE
		for x in reversed(tree):
			x.handleEvent(event)
			
		return True

	def getTree(self):
		current = self
		l = []
		
		while current.owner != None:
			l.append(current.owner)
			current = current.owner
			
		l.reverse()
		
		return l
		
	def addEventListener(self, event, listener, useCapture=False):
		type = event.type
		if type not in self.listeners:
			self.listeners[type] = []
			
		self.listeners[type].append((listener, useCapture))
		
	def removeEventListener(self, event, listener, useCapture=False):
		type = event.type
		self.listeners[type].remove((listener, useCapture))
		
	def handleEvent(self, event):
		event.currentTarget = self
		if event.type in self.listeners:
			for f, useCapture in self.listeners[event.type]:
				if event.phase == CAPTURING_PHASE and useCapture:
					f(event)
				elif event.phase == BUBBLING_PHASE and not useCapture:
					f(event)
				elif event.phase == AT_TARGET:
					f(event)


class Event(object):
	def __init__(self, type, bubbles=True, cancelable=False):
		self.type = type
		self.bubbles = bubbles
		self.cancelable = cancelable
		self.phase = None
		
	def __call__(self, *args, **kwargs):
		return self.__class__(self.type, *args, **kwargs)
	