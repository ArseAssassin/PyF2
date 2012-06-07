from lib import *

def defaultLibrary():
	return Lib(
		Direction("east", 'e'),
		Direction("west", 'w'),
		Direction("north", 'n'),
		Direction("south", 's'),
		Direction("northeast", 'ne'),
		Direction("northwest", 'nw'),
		Direction("southeast", 'se'),
		Direction("southwest", 'sw'),
		Direction("up"),
		Direction("down"),
		Article("a"),
		Article("an"),
		Article("the"),
		Article("that"),
		Preposition("with", "using", 'along'),
		Verb('go', 'walk', 'run', 'travel'),
		Verb('open'),
		Verb('close', 'shut'),
		Verb('turn off'),
		Verb('turn on'),
		Verb('take', 'pick up', "get"),
		Verb('examine', 'look at', 'look', 'x', 'describe'),
		Word('inventory', 'inv', 'i'),
		Attack('hit', 'strike', 'punch')
	)