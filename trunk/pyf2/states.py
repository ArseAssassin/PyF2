from io.context import Context
from io.output import Output, OutputClosed
from world.events.events import EventDispatcher, Event
from world.events import game_events

class StateEvent(Event):
	def __init__(self, type, state=None, *args, **kwargs):
		Event.__init__(self, type, *args)
		self.state = state

KILL = Event("kill")
SWITCH = StateEvent("change")

class State(EventDispatcher):
	def __init__(self):
		EventDispatcher.__init__(self)
		self.prompt = "> "
		self.previous = None
		
	def handle(self, input):
		raise Exception("Unimplemented")
		
	def kill(self):
		self.dispatchEvent(KILL())
		
	def switch(self, value):
		self.dispatchEvent(SWITCH(state=value))
		
		
class Controlled(State):
	def __init__(self, actor):
		State.__init__(self)
		self.actor = actor
		
	def handle(self, input):
		input.actor = self.actor
		
		context = Context(
			input=input,
			actor=self.actor,
			game=self.actor.game
		)
		
		output = Output(context)
		scope = self.actor.getScope()
		
		
		try:
			self.handleWith(self.actor.getScope().getTopmost(), input, output)
			
			for x in input.items:
				if x in scope:
					x.owner.dispatchEvent(game_events.CHILD_HANDLE())
					self.handleWith(x, input, output)

			self.handleWith(self.actor, input, output)

			self.actor.handleError(input, output)
			
		except OutputClosed, e:
			pass
			
		return output
		
	def handleWith(self, item, input, output):
		item.noun.add('*self')
		e = None # will be used to store OutputClosed if raised
		handler = lambda x: x.handler(input, output)
		try:
			item.addEventListener(game_events.REQUEST_HANDLING, handler)
			item._handle(input, output)
		except OutputClosed, e:
			pass

		item.removeEventListener(game_events.REQUEST_HANDLING, handler)
		item.noun.remove('*self')
		
		if e:
			raise e
		
	def getScopedItems(self):
		scope = self.getScope()
		return scope.topDown()
	
	def getScope(self):
		return self.actor.getScope()
	