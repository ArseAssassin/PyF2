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
assert i.hashLog() == "d3e02cda75dc3c1f59e66b5d88bcb3044ad8d827"
print 'Test successful'
