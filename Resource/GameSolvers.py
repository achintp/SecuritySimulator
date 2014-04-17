import sys
import json
import pprint
import inspect
import gambit
import gambit.nash

methods = {
	"Compute equilibria of a game using polynomial systems of equations": gambit.nash.ExternalEnumPolySolver,
	"Computes Nash equilibria using extreme point enumeration" : gambit.nash.ExternalEnumMixedSolver,
	"Compute equilibria in a two-player game via linear complementarity" : gambit.nash.ExternalLCPSolver,
	#"Compute equilibria in a two-player constant-sum game via linear programming" : gambit.nash.ExternalLPSolver,
	"Compute Nash equilibria using function minimization":gambit.nash.ExternalLyapunovSolver,
	"Compute equilibria via simplicial subdivision": gambit.nash.ExternalSimpdivSolver,
	"Compute quantal response equilbria": gambit.nash.ExternalLogitSolver
}

def writeToFile(fileHandle, game, results):
	for profiles in results:
		for player in game.players:
			fileHandle.write(str(profiles.__getitem__(player)) + "\n")

def getEquilibrium(fname, infoFile):
	debug = 0
	g = gambit.read_game(fname)
	for player in g.players:
		print player.label, len(player.strategies)

	with open(infoFile) as jFile:
		data = json.load(jFile)

	for pnum, role in enumerate(data['roles']):
		for index, strategy in enumerate(role['strategies']):
			g.players[pnum].strategies[index].label = strategy

	if debug:
		for player in g.players:
			print player.strategies,"\n"

		print list(g.contingencies)
		for i in range(0, len(g.players[0].strategies)):
			for j in range(0, len(g.players[1].strategies)):
				print g[i,j][0],
				print "\t\t\t",
				print g[i,j][1]

	with open("Eq.txt", 'w') as rF:
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
			writeToFile(rF, g, res)
			rF.write("\n\n")


if __name__ == '__main__':
	getEquilibrium(sys.argv[1], sys.argv[2])