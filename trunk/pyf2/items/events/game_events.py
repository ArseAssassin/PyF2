import events

class GameEvent(events.Event):
	def __init__(self, type, done=None):
		events.Event.__init__(self, type)
		self.done = done


class MoveEvent(GameEvent):
	def __init__(self, type, done=None, destination=None):
		GameEvent.__init__(self, type=type, done=done)
		
		self.destination = destination
		

class HandlerEvent(events.Event):
	def __init__(self, type, handler=None):
		events.Event.__init__(self, type)
		self.handler = handler
		

CHILD_ACT = GameEvent("child_act")
CHILD_HANDLE = GameEvent("child_handle")
MOVE = MoveEvent("move")
ACQUIRE = MoveEvent("acquire")
REQUEST_HANDLING = HandlerEvent("request_handling")

GAME_WON = GameEvent("game_won")
GAME_LOST = GameEvent("game_lost")
