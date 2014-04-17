import random


def checkIndex(item):
	try:
		return item[-1]
	except IndexError:
		return 10000


class AgentStrategies(object):
	"""
		Base class for defining the agent strategies. Derive
		the defender and attacker strategy classes from this.
	"""

	def __init__(self, params):
		self.params = params

	def getStrategy(self, strategy):
		if hasattr(self, strategy):
			return getattr(self, strategy)

class AttackerStrategies(AgentStrategies):
	"""
		Defines the agent strategies
	"""

	def __init__(self, params):
		super(AttackerStrategies, self).__init__(params)

	def periodic(self, info, period):
		timePeriod = float(period)
		nextAttack = info['currentTime'] + timePeriod

		attackOrder = sorted(info['resourceInfo'].items(), key = lambda x: x[1]['Probes till now'])

		namesList = []
		for k,v in info['resourceInfo'].iteritems():
			namesList.append(k)

		random.seed()
		index = random.randint(0, len(namesList)-1)
		#print "Random server is " + namesList[index]
		#Delete the entries where the attacker already has ciontrol 
		nextAction = (nextAttack, attackOrder[index])
		return nextAction


class DefenderStrategies(AgentStrategies):
	"""
		Defines the defender strategies
	"""
	def __init__(self, params):
		super(DefenderStrategies, self).__init__(params)

	def periodic(self, info, period):
		"""
		info = { 
			currentTime: v,
			resourceInfo:{
				name: report
			}
		}
		"""
		timePeriod = float(period)
		nextReimage = info['currentTime'] + timePeriod

		defendOrder = sorted(info['resourceInfo'].items(), key = lambda x: x[1]['Probes till now'])
		nextAction = (nextReimage, defendOrder[-1])
		return nextAction

	def periodicRand(self, info, period):
		timePeriod = float(period)
		nextReimage = info['currentTime'] + timePeriod

		resList = info['resourceInfo'].items()

		random.seed()
		index = random.randint(0, len(resList)-1)

		nextAction = (nextReimage, resList[index])
		return nextAction

	def probeCount(self, info, threshold):
		"""
			DON'T USE. If compromise succeeds without threshold
			being crossed, defender never reimages that server.
		"""
		tr = float(threshold)
		#Sort by increasing order of probes executed
		defendOrder = sorted(info['resourceInfo'].items(), key = lambda x: x[1]['Probes till now'])
		maxServer = defendOrder[-1]

		#Check for threshld being crossed
		if (maxServer[1])['Probes till now'] >= threshold:
			nextAction = (info['currentTime'], maxServer)
			return nextAction
		else:
			return -1

	def probeCountTime(self, info, params):
		parts = params.split('_')
		tr = float(parts[0])
		tLim = float(parts[1])

		#Sort by increasing order of probes executed
		probeOrder = sorted(info['resourceInfo'].items(), key = lambda x: x[1]['Probes till now'])
		maxServer = probeOrder[-1]

		#Check if threshold crossed
		if (maxServer[1])['Probes till now'] >= tr:
			#print "Defender action on probe threshold"
			nextAction = (info['currentTime'], maxServer)
			return nextAction
		else:
			#Find all the servers that have been probed since reimage
			probeList = [item for item in probeOrder if item[1]['Probes till now'] > 0]
			#Sort by increasing order of last time probe was executed
			if(probeList):
				execOrder = sorted(probeList, key = lambda x: checkIndex(x[1]['Probe History']))
				maxServer = execOrder[0]
				#Check if crossing the threshold
				if(info['currentTime'] - maxServer[1]['Probe History'][-1] >= tLim):
					#print "Defender action on time threshold"
					nextAction = (info['currentTime'], maxServer)
					return nextAction
				else:
					nextTime = maxServer[1]['Probe History'][-1] + tLim
					#print "defender should check at " + str(nextTime)
					nextAction = (nextTime, maxServer)
					return nextAction
			return -1