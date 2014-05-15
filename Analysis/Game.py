import copy
import pprint
import itertools
import numpy as np
import collections

class Game(dict):
	"""
	Generic description of a game.
	Includes:
	roles = list of roles
	players = dict of roles:player count
	strategies: dict of roles: strategies
	payoffs = list tuples having tuples with
		(r, s, payoff) values
	"""

	def __init__(self, roles=[], players={}, strategies={}, payoffs=[], debug=0):
		self.roles = sorted(set(roles))
		self.debug = debug
		self.players = {r:players[r] for r in self.roles}
		self.strategies = {r:tuple(sorted(set(map(str, \
			strategies[r])))) for r in self.roles}

		self.numStrategies = [len(self.strategies[r]) \
			for r in self.roles]

		self.roleInd = {i:r \
			for i,r in enumerate(self.roles)}
		self.stratInd = {r:{s:i \
			for i,s in enumerate(self.strategies[r])} \
			for r in self.roles}

		#Payoff mat is att_str x def_str
		self.adjMat = [['inf' \
			for i in range(self.numStrategies[1])] \
			for j in range(self.numStrategies[0])]
		self.payoffMat = copy.deepcopy(self.adjMat)

		if payoffs:
			for profile_data in payoffs:
				self.addProfile(profile_data)

	def addProfile(self, profile_data):
		if len(profile_data) == 2:
			#two player game
			ind = [-1,-1]
			for item in profile_data:
				for k,v in self.roleInd.iteritems():
					if item[0] == v:
						ind[k] = (self.stratInd[item[0]])\
							[item[1]]
			self.adjMat[ind[0]][ind[1]] = 1

	def consensus(self, oldList):
		newList = []
		it = itertools.combinations(oldList,2)
		for item in it:
			inter = item[0][1].intersection(item[1][1])
			if(inter):
				un = item[0][0].union(item[1][0])
				newItem = [un, inter]
				if newItem not in newList and \
				newItem not in oldList:
					newList.append(newItem)

		return newList

	def absorption(self, oldList, newList):
		# if self.debug:
		# 	pprint.pprint(oldList)
		# 	pprint.pprint(newList)
		remainList = []
		for item in oldList:
			for comp in newList:
				# pprint.pprint(item)
				# pprint.pprint(comp)
				if not(item[0]<=comp[0] and \
				item[1]<=comp[1]):
					if item not in remainList:
						remainList.append(item)
				else:
					if item in remainList:
						remainList.remove(item)
					break

		if self.debug:
			print "End absorption"
			pprint.pprint(remainList)
			pprint.pprint(newList)

		remainList.extend(newList)
		return remainList

	def findCliques(self, oldList=[]):
		#Based on a variation of the consensus algorithm
		#First make the initial att_str -> def_str
		oldList = []
		newList = []

		for i in range(0, self.numStrategies[0]):
			t = set(i)
			r = set()
			for j in range(0, self.numStrategies[1]):
				if(self.adjMat[i][j] == 1):
					r.add(j)
			if r:
				oldList.append([t,r])

		if self.debug:
			print oldList

		#Consensus stage
		newList = self.consensus(oldList)
		while(newList):
		#Absorption stage
			oldList = self.absorption(oldList, newList)
			if self.debug:
				pprint.pprint(oldList)
			newList = self.consensus(oldList)

		return oldList

	def printData(self):
		pprint.pprint(self.roles)
		pprint.pprint(self.players)
		pprint.pprint(self.strategies)
		pprint.pprint(self.roleInd)
		pprint.pprint(self.stratInd)
		pprint.pprint(self.adjMat)


if __name__ == '__main__':
	roles = ['ATT','DEF']
	players = {r:1 for r in roles} 
	strategies = {r:['temp'+str(i) \
		for i in range(3)] for r in roles}
	payoffs = [((roles[0], strategies[roles[0]][0], 1),\
		(roles[1], strategies[roles[1]][1], 1))]
	pprint.pprint(payoffs)
	g = Game(roles, players, strategies, payoffs, 0)
	g.printData()

	testList = [[set(['a']), set(['d', 'e', 'f'])],\
	[set(['b']), set(['d', 'e', 'f'])],[set(['c']), \
	set(['g', 'e', 'f'])]]
	pprint.pprint(g.findCliques(testList))