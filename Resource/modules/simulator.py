import copy
import time
import json
import random
import pprint
import agents 
import strategies
import knowledge_state

class Simulator(object):
	"""Main simulator class"""
	def __init__(self, args):
		"""Pass in args as dict. Include:
		startTime
		endTime
		resourceList
		attackerList
		defenderList
		dtCost
		prCost
		DEF - []
		ATT - []
		"""

		#Initialize state variables
		