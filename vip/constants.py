from enum import IntEnum

class Action(IntEnum):
	TAB = 1 << 0
	DB = 1 << 1
	FILE = 1 << 2
