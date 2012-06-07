import cod
from pyf2 import debug

i = debug.Debugger()
i.loadGame(cod.game)

i.test(
	'''
	x yourself
	n
	s
	read message
	n
	w
	x hook
	hang cloak on hook
	x hook
	e
	s
	read message
	'''
)
assert i.hashLog() == "e70eebc23cd5b1402c1f785b74aa9d147b39a405"
print 'Test successful'
