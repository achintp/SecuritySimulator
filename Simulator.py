import copy
import time
import random
import json
from pprint import pprint
import Resource.Utility as Utility
import Resource.Strategies as Strategies
import Resource.StateClasses as StateClasses
import Resource.AgentClasses as AgentClasses

class SimulateCyberScenario(object):
	"""
		Simulator class, framework for running games
	"""
	def __init__(self, args):

		"""
			Pass in args as a dict. Include:
			startTime - event horizon start
			endTime - event horizon end
			resourceList - list of resource names
			attackerList - k,v pair of name, strategy
			defenderList - k,v pair of name, strategy
			dtCost - cost of unit downtime
			prCost - cost of unit probe
			DEF - []
			ATT - []
		"""
	#Initialize the state variable. Internally will initialize
	#the resources
		self.params = {}
		self.params['startTime'] = args['startTime']
		self.params['endTime'] = args['endTime']
		self.params['currentTime'] = 0
		self.params['downTime'] = args['downTime']
		self.attackerList = []
		self.defenderList = []
		self.debug = 0
		self.params['resourceReports'] = {}
		self.gameState = 1
		self.askAtt = True
		self.askDef = True
		self.simType = 0
		self.attSwitch = True
		self.defSwitch = True
		token = 'probe'

		self.defStrategy = None
		for k,v in args['defenderList'].iteritems():
			self.defStrategy = v
			if token in v:
				self.simType = 1

		self.attStrategy = None
		for k,v in args['attackerList'].iteritems():
			self.attStrategy = v

		if self.defStrategy == 'No-Op':
			self.defSwitch = False
		if self.attStrategy == 'No-Op':
			self.attSwitch = False

		#Construct utility parameters
		self.utilParams = {}
		self.utilParams['dtCost'] = args['dtCost']
		self.utilParams['prCost'] = args['prCost']
		self.utilParams['DEF'] = args['DEF']
		self.utilParams['ATT'] = args['ATT']
		self.utilParams['downTime'] = args['downTime']

		#Initialize the event queue
		f = (self.params['endTime'], 0, -1)
		self.eventQueue = [f]
		#Initialize the state variable
		self.state = StateClasses.State(**{'ResourceList':args['ResourceList'], 'alpha':args['alpha']})
		self.params['resourceReports'] = self.state.resourceReportsList
		#resourceReports = {
		# 'name of resource':{
		# 	Status:v, 
		# 	Name:v, 
		# 	Probes till now:v, 
		# 	total probes:v, 
		# 	prob:v, 
		# 	reimage count:v, 
		# 	total downtime:v,
		# 	control:v}
		# }

		#Initialize the agents
		for k,v in args['attackerList'].iteritems():
			d = {
				'name':k,
				'strategy':v,
				'resourceList':args['ResourceList'],
				'time': self.params['currentTime']
			}
			self.attackerList.append(AgentClasses.Attacker(**d))

		for k,v in args['defenderList'].iteritems():
			d = {
				'name':k,
				'strategy':v,
				'resourceList':args['ResourceList'],
				'time': self.params['currentTime']
			}
			self.defenderList.append(AgentClasses.Defender(**d))

			#print "Simulator set up. The resources are "
			#for name in args['ResourceList']:
			#	print name
			#print "\nThe players are " + self.attackerList[0].name + " and " +\
			#self.defenderList[0].name

		if(self.debug):
			print self.attackerList
			print self.defenderList

	def askAttacker(self):
		"""
			Asks the attacker about the next attack.
			Adds next event to the eventQueue
			Update the information the agent has and then
			ask for the next action
		"""
		d = dict(self.params['resourceReports'])
		d['time'] = self.params['currentTime']
		for att in self.attackerList:
			att.updateInformation(d)
			nextEvent = att.getAction()

			for index, items in enumerate(self.eventQueue):
				if items[2] == 0:
					#In case pure perodic, just replace with
					#existing time of next attack
					if 'pure' in self.attStrategy:
						temp = list(nextEvent)
						temp[0] = items[0]
						nextEvent = tuple(temp)					
					self.eventQueue.pop(index)

			if nextEvent[0] == -1:
				#There doesn't exist a next attacker event
				#Queue up for p time from the current time
				temp = list(nextEvent)
				if 'Decept' in self.attStrategy:
					temp[0] = self.params['currentTime'] + float((self.attStrategy.split('-')[1]).split('_')[0])
				else:	
					temp[0] = self.params['currentTime'] + float(self.attStrategy.split('-')[1])
				nextEvent = tuple(temp)
				# if self.debug:
				# 	print "Assigned new attack"
				# 	pprint(nextEvent)
			self.eventQueue.append(nextEvent)

		self.sortEventQueue()

		if(self.debug):
			print "After asking attacker\n\n"
			print self.eventQueue
			print "\n\n"

	def askDefender(self):
		"""
			Analogous to attacker 
		"""
		#If existing defender event in queue, then keep that
		nextTime = None
		for items in self.eventQueue:
			if(items[2] == 1): 
				#print "Defender Action exists-------------------"
				#print items
				if 'pure' in self.defStrategy:
						nextTime = items[0]
						self.eventQueue.remove(items)
						continue
				if(items[1] == None or self.simType == 1):
					self.eventQueue.remove(items)
				else:
					if self.debug:
						print "Defender action exists"
					if 'pure' in self.defStrategy:
						# print "This is never executed so I just left it in LOL"
						continue
					else:
						return

		d = dict(self.params['resourceReports'])
		d['time'] = self.params['currentTime']
		for defs in self.defenderList:
			defs.updateInformation(d)
			nextEvent = defs.getAction()
			if nextEvent == -1:
				if self.debug:
					print "No defender Action"
				return 0
			else:
				if 'pure' in self.defStrategy:
					if nextTime:
						temp = list(nextEvent)
						temp[0] = nextTime
						nextEvent = tuple(temp)
			self.eventQueue.append(nextEvent)

		self.sortEventQueue()
		if(self.debug):
			print "After asking defender\n\n"
			print self.eventQueue
			print "\n\n"
		return 1

	def sortEventQueue(self):
		self.eventQueue = sorted(self.eventQueue)

	def executeAction(self):
		"""
			Picks the next action from the event queue and
			executes it.
		"""
		#Check whether the event horizon has ended
		nextEventTime = self.eventQueue[0][0]
		if(nextEventTime > self.params['endTime']):
			print "Game over"
			self.gameState = 0
			return
		else:
			#if more than one event are queued at the same time,
            #shuffle them randomly
			if len(self.eventQueue) > 2:
				if(self.eventQueue[0][0] == self.eventQueue[1][0]):
					self.shuffleEvents()
			#remove next event from the queue
			it = self.eventQueue.pop(0)
			if self.debug:
				print "Event popped-------------------"
				print it

			self.params['currentTime'] = it[0]
			if self.debug:
				print "The time is: " + str(self.params['currentTime'])
			if(it[2] == 0 or it[2] == 1):
				if(it[1] != None):
					res = self.state.getResource(*[it[1][0]])
					r = res[it[1][0]]
				else:
					#Handles the dummy event. For now only attacker
					#has a dummy event. Makes sure attacker queues
					#new action
					if(self.debug):
						print "Dummy handled"
					if(it[2] == 0):
						if self.debug:
							print "attacker dummy"
						self.askAtt = True
						self.askDef = False
						return
					if(it[2] == 1):
						if self.debug:
							print "Defender Dummy"
						self.askDef = True
						self.askAtt = False
					return
			elif(it[2] == 2):
				res = self.state.getResource(*[it[1]])
				r = res[it[1]]
			elif(it[2] == -1):
				#print "Game is over\n\n"
				self.gameState = 0
				return 0
			else:
				raise Exception("Unknown command executed")
			

			if(self.debug):
				print "Resource acquired--------------"
				print r

			if(it[2] == 1):
				#Reimage event, defender action
				#Grab defender, make them execute reimage on
				#mentioned resource
				#print "Reimaging now?----------------------"
				if self.debug:
					print "D is reimaging " + r.name

				if(r.controlledBy == "ATT"):
					self.askAtt = True
					if self.debug:
						print "Compr server att knows"
				else:
					self.askAtt = False

				d = self.defenderList[0]
				t = d.reImage(r)
				r.lastReImage = self.params['currentTime']
				timePair = []
				timePair.append(self.params['currentTime'])
				r.downTime.append(timePair)
				self.askDef = True				
				 #remove from attackers control list
				a = self.attackerList[0]
				a.loseControl([it[1][0]])

				 #add downtime event
				waketime = self.params['currentTime'] + self.params['downTime']
				self.eventQueue.append((waketime, it[1][0], 2))
				if self.debug:
					print r.name + " is DOWN. Will be up again at " + str(waketime)

				 #modify inactive list of state
				self.state.inactiveResources[it[1][0]] = self.state.activeResources[it[1][0]]
				del self.state.activeResources[it[1][0]]
				#self.flushEventQueue(r.name)
				#print self.state.activeResources
				#print self.state.inactiveResources

				self.sortEventQueue()
			elif(it[2] == 0):
				#Probe event followed by attack event
				#Grab attacker, execute probe, then execute attack
				if(r.name in self.state.inactiveResources):
					#Skips the server if it finds it went down in between
					#Instead tries to pick new server that is active and
					#not compromised
					if self.debug:
						print "Skipping att act on " + r.name + " since down"
					if not self.state.activeResources:
						if self.debug:
							print "No active servers to attack"
						self.askAtt = True
						self.askDef = True
						return
					p = random.choice(self.state.activeResources.keys())
					if(self.state.activeResources[p].controlledBy == "ATT"):
						if self.debug:
							print "Changing again since" + p + " is already compromised"
						x = [tvar for tvar in self.state.activeResources]
						x.remove(p)
						if not x:
							#There are no uncompromised servers active
							self.askAtt = True
							self.askDef = True
							return
						p = x[0]
						if self.debug:
							print "New chosen as" + p + " tack."
						if(self.state.activeResources[p].controlledBy == "ATT"):
							#Both active servers are compromised
							if self.debug:
								print "Even this is compromised. No action possible"
							self.askAtt = True
							self.askDef = True
							return
					res = self.state.getResource(p)
					r = res[p]
					if self.debug:
						print "Changing choice to\n" + r.name
				# else:
				if self.debug:
					print "A is probing and attacking " + r.name
				a = self.attackerList[0]
				# r = self.state.getResource(*list(it[1][0]))
				r = a.probe(r)
				r.probeHistory.append(self.params['currentTime'])
				a.currentTime = self.params['currentTime']
				r = a.attack(r)
				self.askDef = True
				self.askAtt = True
			elif(it[2] == 2):
				#Downtime over for resource
				if self.debug:
					print it[1] + " is up and running again"
				self.state.activeResources[it[1]] = self.state.inactiveResources[it[1]]
				del self.state.inactiveResources[it[1]]
				#print "Resource Activated---------------------\n\n"
				#print self.state.activeResources
				r.changeStatus(1)
				r.downTime[-1].append(self.params['currentTime'])
				r.totalDowntime += self.params['downTime']
				self.askDef = True
				self.askAtt = False

				#print "Resource up and running"
				#print r.report()
			elif(it[2] == -1):
				#print "Game is over"
				self.gameState = 0
				return 0

	def updateInformation(self):
		#print "Updating the state information\n"
		self.state.updateState(self.params['currentTime'])
		info = {}
		# info['resourceInfo'] = self.state.resourceReportsList
		info = self.state.resourceReportsList
		if(self.debug):
			print "Updating resource reports to\n"
			print self.state.resourceReportsList
			print "\n"

		self.params['resourceReports'] = self.state.resourceReportsList
		info['time'] = self.params['currentTime']
		self.attackerList[0].updateInformation(info)
		self.defenderList[0].updateInformation(info)
		#self.printEvents()

	def flushEventQueue(self, name):
		#print "Fush " + name
		#rm = False
		for index, items in enumerate(self.eventQueue):
			#print items
			if items[2] == 0:
				if items[1][0] == name:
					#print items, index
					rm = index
		try:
			t = self.eventQueue.pop(rm)
			#print "Removed"
			#print t
		except UnboundLocalError:
			#self.printEvents()
			pass

	def shuffleEvents(self):
		cTime = self.eventQueue[0][0]
		count = 0
		for i in range(1,3):
			if(self.eventQueue[i][0] == cTime):
				count += 1
		rep = random.randint(0, count)
		temp = self.eventQueue.pop(rep)
		self.eventQueue.insert(0, temp)


	def printEvents(self):
		print "\n-----------------------------------------------------------"
		print "The events queue is"
		for events in self.eventQueue:
			print "At time " + str(events[0]),
			if events[2] == 0:
				print self.attackerList[0].name + " will probe " + events[1][0]
			elif events[2] == 1:
				print self.defenderList[0].name + " will reimage " + events[1][0]
			elif events[2] == -1:
				print "Game will end."
			elif events[2] == 2:
				print events[1] + " will reactivate."
		print "-----------------------------------------------------------\n"	

	def printAgentMoves(self):
		print "\n"
		for item in self.eventQueue:
			if item[2] == -1:
				print "Game ends at " + str(item[0])
			elif item[2] == 0:
				print "Attacker move at " + str(item[0])
			elif item[2] == 1:
				print "Defender move at " + str(item[0])
			elif item[2] == 2:
				print "Server waking at " + str(item[0])
			else:
				print "WTF"

	def Simulate(self):
		#Start the simulation and keeps it running
		#Implements normal wall clock periodic strategy
		if self.simType == 0 or self.simType == 1:
			# with open('res.json', 'w') as jFile:
			while(self.gameState):
				self.updateInformation()
				if self.attSwitch:
					if(self.askAtt):
						self.askAttacker()
				if self.defSwitch:
					if(self.askDef):
						self.askDefender()
				# json.dump(self.eventQueue, jFile)
				# self.printAgentMoves()
					# print "\n"
				self.executeAction()


		#Hybdrid defender strategy of #of probes and time
		#since last probe
		if self.simType == 2:
			if self.debug:
				print "Initializing sim 2"
			while(self.gameState):
				self.updateInformation()
				if self.askAtt:
					self.askAttacker()
				self.executeAction()
 				if self.askDef:
					self.updateInformation()
					act = self.askDefender()
					if act:
						self.executeAction()
						self.askAtt = 1

		self.params['currentTime'] = self.params['endTime']
		self.updateInformation()

		self.stateHistory = self.state.stateHistory
		u = Utility.Utility(self.utilParams)

		utilFunc = u.getUtility('simpleCIA')
		payoff = utilFunc(self.stateHistory)

		if(self.debug):
			for it in sorted(self.stateHistory.items()):
				print it
				print '\n\n'

		return payoff