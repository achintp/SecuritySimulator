import sys
import Game
import pprint
from decimal import Decimal
import itertools
import Donimation
import gambit
import gambit.nash

methods = {
	# "Compute equilibria of a game using polynomial systems of equations":\
	# 	 gambit.nash.ExternalEnumPolySolver,
	"Computes Nash equilibria using extreme point enumeration":\
		 gambit.nash.ExternalEnumMixedSolver
	# "Compute equilibria in a two-player game via linear complementarity":\
	# 	 gambit.nash.ExternalLCPSolver,
	# "Compute Nash equilibria using function minimization":\
	# 	gambit.nash.ExternalLyapunovSolver,
	# "Compute equilibria via simplicial subdivision": \
	# 	gambit.nash.ExternalSimpdivSolver,
	# "Compute quantal response equilbria": \
	# 	gambit.nash.ExternalLogitSolver
}

class gameData:
	def __init__(self, roles, numStrat, strat, payoff):
		self.roles = roles
		self.numStrat = numStrat
		self.strat = strat
		self.payoff = payoff

def writeToFile(fileHandle, game, results):
	for profiles in results:
		for player in game.players:
			fileHandle.write(str(profiles.__getitem__(player)) + "\n")

def writeEquToFile(fileHandle, game, results):
	for profiles in results:
		for players in game.players:
			l = profiles.__getitem__(players)
			strats = players.strategies
			for pair in zip(l, strats):
				if pair[0] > 0:
					fileHandle.write(pair[1].label + "-" +str(pair[0]) + "\t")
			fileHandle.write("\n")
		fileHandle.write("\n\n")
	fileHandle.write("\n\n")


def solveGame(data, outname):
	"""
		data should be an object containing:
		roles = list of roles
		numStrat = number of strategies per role
		strat = {role: {index : strategy}}
		payoff = list of list of payoffs
	"""
	g = gambit.new_table([data.numStrat[0], \
		data.numStrat[1]])
	g.title = outname

	for i,r in enumerate(data.roles):
		g.players[i].label = r
		for j in range(data.numStrat[i]):
			g.players[i].strategies[j].label = data.strat[r][j]

	for item in itertools.product(range(data.numStrat[0]),\
		range(data.numStrat[1])):
		g[item[0],item[1]][0] = Decimal(data.payoff[item[0]][item[1]][0])
		g[item[0],item[1]][1] = Decimal(data.payoff[item[0]][item[1]][1])

	for profile in g.contingencies:
		print g.players[0].strategies[profile[0]].label, \
			g.players[1].strategies[profile[1]].label, \
			g[profile][0], g[profile][1]

	with open("Eq-" + outname + ".txt", 'w') as rF:
		rF.write("Mapping of player strategies\n")
		for player in g.players:
			rF.write(player.label + ":[")
			for strategy in player.strategies:
				rF.write(strategy.label + " ")
			rF.write("]\n")
		rF.write("\n\n")
		for desc, func in methods.iteritems():
			rF.write(desc + "\n")
			solver = func();
			res = solver.solve(g)
			writeEquToFile(rF, g, res)
			# writeToFile(rF, g, res)
			rF.write("\n\n")

if __name__ == '__main__':
	roles = ["ATT", "DEF"]
	numStrat = [3,3]
	strat = {
	"ATT":{
		i:"ATT"+str(i) for i in range(3)
		},
	"DEF":{
		i:"DEF"+str(i) for i in range(3)	
		}
	}
	payoff = [
	[(3,1), (2,4), (1,2)],
	[(1,1), (5,4), (1,9)],
	[(3,4), (2,1), (1,1)]
	]

	d = gameData(roles, numStrat, strat, payoff)
	solveGame(d, 'something')

