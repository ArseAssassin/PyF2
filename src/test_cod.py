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
assert i.hashLog() == "1dcf7903b2184e9cadd08624e51e035fbd028ade"
print 'Test successful'
