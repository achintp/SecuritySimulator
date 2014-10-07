import Strategies

class Agent(object):
	"""
		Base Agent class
	"""
	def __init__(self, **kwargs):
		"""
			Takes dict as argument, including
			name:
			strategy:
			resourceList:
			time:
		"""
		#Initialize values
		self.name = kwargs['name']
		st = kwargs['strategy'].split('-')
		self.strategy = st[0]
		self.stparam = st[1]
		# self.strategy = kwargs['strategy']
		self.resourceList = kwargs['resourceList']
		self.currentTime = kwargs['time']
		self.previousTime = -1

		#Initializee empty parameters
		self.actionHistory = {}
		self.controlList = {}		
		self.resourceInfo = {}

		self.debug = 0

	def updateInformation(self, info):
		"""
			Updates the information that the attacker has about the current state.
			A dict of parameters should be passed in. Include:
			name of resource: info about resource
			time: current time

		"""
		for name in self.resourceList:
			self.resourceInfo[name] = info[name]
		# print self.resourceInfo
		# print "//////////////////////////////////////////////////////////\n\n"

		self.previousTime = self.currentTime
		self.currentTime = info['time']

		if(self.debug):
			print "Reporting from inside updateInformation for ";
			if hasattr(self, 'type'):
				print self.type
			for k,v in self.resourceInfo.iteritems():
				print k + "\n"
				print v
			print "Current time - " + str(self.currentTime)
			print "Previous TIme - " + str(self.previousTime)

	def getParams(self, *param):
		"""Should return parameters. Not implemented for now."""

	def setParams(self, **params):
		"""Have to implement. I think I'm going to need to convert the parma list to a dictionary structure"""

	def decideAction(self):
		"""
			Decides the next action to be taken. Should be run after the state variables are 
			updated and information is updated. 
		"""
		#Placeholder implementation for strategy. Not sure exactly how to do it since the cost of
		#putting a probe has to be incorporated

class Attacker(Agent):
	"""
	Defines the attacker agent. Inherits from agent base class
	"""
	def __init__(self, **params):
		super(Attacker, self).__init__(**params)
		self.type = "ATT"
		self.setStrategy()

	def setStrategy(self):
		"""
		To set the strategy, first set the strategy attribute of the agent, then
		call this.
		"""
		if hasattr(self, 'strategy'):
			a = Strategies.AttackerStrategies({})
			self.decideAction = a.getStrategy(self.strategy)

		if(self.debug):
			print "Strategy set"

	def getAction(self):
		#Remove the resources that are on the controlled list and give the rest to the strategy
		#function for deciding
		# d = dict(self.resourceInfo)
		d = {}	

		for k,v in self.resourceInfo.iteritems():
			if (v['Status'] != 'DOWN'): 
				d[k] = v
		# print "/////////////////////////////////////////////"
		# print d
		# print "////////////////////////////////////////////\n\n"

		if self.debug:
			print "Control List--------------------------"
			print self.controlList
			print d

		for k,v in self.controlList.iteritems():
			if 'Decept' in self.strategy:
				if(self.currentTime - float(self.resourceInfo[v]['Probe History'][-1]) < float((self.stparam.split('_'))[1])):
					del d[v]
				else:
					if self.debug:
						print "Considering "+v+"with last probe "+str(self.resourceInfo[v]["Probe History"][-1]),
						print "and current time "+str(self.currentTime)
			else:
				del d[v]

		if not d:
			# print "/////////////////EMPTY///////////////\n\n"
			if 'Decept' in self.strategy:
				per = self.stparam.split('_')[0]
			else:
				per = self.stparam
			if 'pure' in self.strategy:
				return (-1, None, 0)
			else:
				return (self.currentTime + float(per), None, 0)
			
		c = {}
		c['resourceInfo'] = d
		c['currentTime'] = self.currentTime
		action = self.decideAction(c, self.stparam)
		action = action + (0,)
		if(self.debug):
			print action
		return action

	def probe(self, resource):
		"""
		Probe function of attacker. Takes the resource and changes probe counter and
		probability of compromise. Followed by atomic time attack.
		"""
		resource.probesTillNow += 1
		resource.totalProbesTillNow += 1
		# resource.probeHistory.append(self.currentTime)
		resource.incrementProb()
		resource.changeStatus(0)

		if(self.debug):
			print resource.report()

		return resource

	def attack(self, resource):
		"""Attack following probe. Give the resource as input
		"""
		if(resource.isCompromised()):
			resource.changeStatus(-1)
			resource.controlledBy = "ATT"
			if resource.name not in self.controlList.values():
				self.controlList[self.currentTime] = resource.name
			#print "Compromised " + resource.name

		self.actionHistory[self.currentTime] = resource.name
		return resource

	def loseControl(self, names):
		"""
		Removes resources from control list. Call from env after reimage.
		"""
		if self.debug:
			print self.controlList

		for name in names:
			# del self.controlList[name]
			self.controlList = {key: value for key, value in self.controlList.items() if value != name}

		if self.debug:
			print "Attacker lost control. Has control of:\n"
			print self.controlList

class Defender(Agent):
	"""
	Defender, inherits from Agent class. Give requisite input
	"""
	def __init__(self, **params):
		super(Defender, self).__init__(**params)
		self.type = "DEF"
		self.setStrategy()

	def setStrategy(self):
		"""
		Analogous to get strategy for the attacker class.
		"""
		if hasattr(self, 'strategy'):
			a = Strategies.DefenderStrategies({})
			self.decideAction = a.getStrategy(self.strategy)

	def getAction(self):
		# d = dict(self.resourceInfo)
		d = {}

		for k,v in self.resourceInfo.iteritems():
			if (v['Status'] != 'DOWN'): 
				d[k] = v

		if not d:
			# print "/////////////////EMPTY///////////////\n\n"
			if 'periodic' in self.strategy or 'Periodic' in self.strategy:
				return (self.currentTime + float(self.stparam), None, 1)
			else:
				return -1

		targets = {}
		targets['resourceInfo'] = d
		targets['currentTime'] = self.currentTime
		action = self.decideAction(targets, self.stparam)
		if action == -1:
			return action
		action = action + (1,)
		if(self.debug):
			print action

		return action

	def reImage(self, resource):
		#print "Reimaging--------------------" + resource.name+ "\n"
		resource.reimageCount += 1
		resource.probCompromise = 0
		resource.probesTillNow = 0
		resource.controlledBy = "DEF"
		resource.changeStatus(2)
		self.actionHistory[self.currentTime] = resource.name
		# downtime = 5

		#print resource.report()

		return resource






