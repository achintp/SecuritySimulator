import copy
import pprint
import itertools
import numpy as np
import collections
import Donimation
import SolveGame

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
		self.payoffMat = [[(None, None) \
			for i in range(self.numStrategies[1])] \
			for j in range(self.numStrategies[0])]
		self.cliques = None

		if payoffs:
			for profile_data in payoffs:
				self.addProfile(profile_data)
		if self.debug:
				# pprint.pprint(self.adjMat)
				pprint.pprint(self.payoffMat)

	def addProfile(self, profile_data):
		if len(profile_data) == 2:
			#two player game
			ind = [-1,-1]
			values = [None for i in range(2)]
			for item in profile_data:
				for k,v in self.roleInd.iteritems():
					if item[0] == v:
						ind[k] = (self.stratInd[item[0]])\
							[item[1]]
						values[k] = item[2]
							
			self.adjMat[ind[0]][ind[1]] = 1
			self.payoffMat[ind[0]][ind[1]] = tuple(values)

	def reduceGame(self):	
		cols = len(self.payoffMat[0])
		rows = len(self.payoffMat)
		#red stands for reduced
		redGame = Donimation.bimatrixDomination(self.payoffMat,\
			rows, cols, 1)
		self.redRows = redGame['redRows']
		self.redCols = redGame['redCols']
		self.payoffMat = redGame['redMat']
		self.redNumStrategies = [len(self.redRows), len(self.redCols)]
		self.redStrat = {}
		for item in zip(self.roles, [redGame['redRows'], redGame['redCols']]):
			self.redStrat[item[0]] = item[1]	

		#Write out the iterated elimination file
		# with open('IteratedElim.txt','r') as inFile:
		# 	with open('IteratedElimStrats.txt', 'w') as outFile:

		#Refactor the matrix
		self.refactorGame()

		if self.debug:
			print "Reduced Game:"
			pprint.pprint(self.redStrat)
			pprint.pprint(self.numStrategies)
			pprint.pprint(self.dominStrats)
			pprint.pprint(self.strategies)
			pprint.pprint(self.payoffMat)
			pprint.pprint(self.adjMat)

	def refactor(self):
		self.numStrategies = self.redNumStrategies
		self.dominStrats = {}
		self.remStrats = {}
		#Re-assign the strategies being used
		for k,v in self.strategies.iteritems():
			t = []
			p = []
			for item in v:
				if self.stratInd[k][item] in self.redStrat[k]:
					t.append(item)
				else:
					p.append(item)
			self.dominStrats[k] = p
			self.remStrats[k] = t
		self.strategies = self.remStrats

		#Refactor the indexing of the strategies
		self.stratInd = {r:{s:i \
			for i,s in enumerate(self.strategies[r])} \
			for r in self.roles}

		#Make the new adjacency matrix
		self.adjMat = [['inf' \
			for i in range(self.numStrategies[1])] \
			for j in range(self.numStrategies[0])]

		empty = (None, None)
		for i in range(self.numStrategies[0]):
			for j in range(self.numStrategies[1]):
				if(self.payoffMat[i][j] != empty):
					 self.adjMat[i][j] = 1

		#print out the dominated strategies
		with open('domStrategies.txt', 'w') as outFile:
			pprint.pprint(self.dominStrats, outFile)
			pprint.pprint(self.remStrats, outFile)

	def refactorGame(self):
		for item in zip(self.numStrategies, self.redNumStrategies):
			if(item[0] != item[1]):
				self.refactor()
				return

	def consensus(self, oldList):
		print "In consensus"
		newList = []
		it = itertools.combinations(oldList,2)
		for item in it:
			print item
			inter = item[0][1].intersection(item[1][1])
			if(inter):
				un = item[0][0].union(item[1][0])
				newItem = [un, inter]
				if newItem not in newList and \
				newItem not in oldList:
					newList.append(newItem)
		# print "newlist:"
		# print newList
		return newList

	def absorption(self, oldList, newList):
		# if self.debug:
		# 	pprint.pprint(oldList)
		# 	pprint.pprint(newList)
		print "in absorption"
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
		print "remaining:"
		print remainList
		return remainList

	def findCliques(self, oldList=[]):
		#Based on a variation of the consensus algorithm
		#First make the initial att_str -> def_str
		oldList = []
		newList = []

		for i in range(0, self.numStrategies[0]):
			t = set([i])
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

		#Convert the list back into strategy names
		cliques = []
		for item in oldList:
			t = []
			for r,agentStr in zip(self.roles, item):
				p = set()
				for strat in agentStr:
					for k,v in self.stratInd[r].iteritems():
						if v == strat:
							p.add(k)
				t.append(p)
			cliques.append(t)
		self.cliques = cliques

		#Store the payoff table of each subgame
		cliquePayoffs = []
		for item in oldList:
			t = [[ (None, None) for i in range(len(item[1]))]\
				for j in range(len(item[0]))]
			for i, aStr in enumerate(item[0]):
				for j, dStr in enumerate(item[1]):
					print i,j,aStr,dStr, len(t), len(t[0])
					t[i][j] = self.payoffMat[aStr][dStr]
			cliquePayoffs.append(t)

		self.cliquePayoffs= cliquePayoffs
		return cliques

	def solveCliqueGames(self):
		cliqueCount = 0
		for pair in zip(self.cliques, self.cliquePayoffs):
			#should be a list of two sets of strategies
			cliques = pair[0]
			#is an array of payoffs
			payoffs = pair[1]

			sNumStrat = [len(cliques[0]), len(cliques[1])]
			strats = {}
			for i,stratSet in enumerate(cliques):
				strats[self.roleInd[i]] = {
					j: strat \
					for j, strat in enumerate(stratSet) 
				}
			cliqueCount += 1
			p = SolveGame.gameData(self.roles, sNumStrat, strats, payoffs)

			if self.debug:
				pprint.pprint(p.roles)
				pprint.pprint(p.numStrat)
				pprint.pprint(p.strat)
				pprint.pprint(p.payoff)
			# try:
			SolveGame.solveGame(p, "clique"+str(cliqueCount))
			# except:
			# 	print "Error"

	def solveGames(self):
		strat = {}

		for roles in self.roles:
			t = {}
			for k,v in self.stratInd[roles].iteritems():
				t[v] = k
			strat[roles] = t

		p = SolveGame.gameData(self.roles, self.numStrategies, strat, self.payoffMat)
		if self.debug:
			pprint.pprint(p.roles)
			pprint.pprint(p.numStrat)
			pprint.pprint(p.strat)
			pprint.pprint(p.payoff)

		SolveGame.solveGame(p, "Something")

	def solveSubGames(self, num):
		t = [[(None, None) for i in range(self.numStrategies[1])] for j in range(int(num))]
		counter = 0
		for triples in itertools.combinations(self.strategies[self.roles[0]], num):
			print "Attacker strategies:- ",
			print triples
			p = []
			m = {}
			n = {}
			for i, atStr in enumerate(triples):
				m[i] = atStr
				for j, dStr in enumerate(self.strategies[self.roles[1]]):
					# p.append(self.payoffMat[self.stratInd[self.roles[0]][atStr]]\
					# 	[self.stratInd[self.roles[1]][dStr]])
					t[i][j] = self.payoffMat[self.stratInd[self.roles[0]][atStr]]\
					[self.stratInd[self.roles[1]][dStr]]
					if j not in n:
						n[j] = dStr
				# t.append(p)
			if self.debug:
				print p
			numStrats = [num, self.numStrategies[1]]
			
			strats = {
				self.roles[0]:m,
				self.roles[1]:n
			}

			p = SolveGame.gameData(self.roles, numStrats, strats, t)
			# if self.debug:
			print "Subgame-" + str(counter)			
			if self.debug:
				pprint.pprint(p.roles)
				pprint.pprint(p.numStrat)
				pprint.pprint(p.strat)
				pprint.pprint(p.payoff)
			SolveGame.solveGame(p, "subGame_" + str(counter))
			counter+=1

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
	strategies = {r:[r+str(i) \
		for i in range(3)] for r in roles}
	payoffs = [
	(('ATT','ATT0',0),('DEF', 'DEF0', 2)),
	(('ATT','ATT0',3),('DEF', 'DEF1', 1)),
	(('ATT','ATT0',2),('DEF', 'DEF2', 3)),
	(('ATT','ATT1',1),('DEF', 'DEF0', 4)),
	(('ATT','ATT1',2),('DEF', 'DEF1', 1)),
	(('ATT','ATT1',4),('DEF', 'DEF2', 1)),
	(('ATT','ATT2',2),('DEF', 'DEF0', 1)),
	(('ATT','ATT2',4),('DEF', 'DEF1', 4)),
	(('ATT','ATT2',3),('DEF', 'DEF2', 2)),
	]
	pprint.pprint(payoffs)
	g = Game(roles, players, strategies, payoffs, 1)
	g.reduceGame()
	pprint.pprint(g.findCliques())
	print "-------------------------"
	pprint.pprint(g.cliquePayoffs)
	g.solveGames()