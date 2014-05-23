import sys
import json
import Game
import pprint

def makeData(fname):
	"""
		Input should be a json file
	"""

	with open(fname, 'r') as jFile:
		data = json.load(jFile)

	roles = []
	players = {}
	strategies = {}

	for item in data['roles']:
		roles.append(item['name'])
		players[item['name']] = item['count']
		t = []
		for strat in item['strategies']:
			t.append(strat)
		strategies[item['name']] = t

	profileData = []
	for profiles in data['profiles']:
		tup = []
		for obs in profiles['symmetry_groups']:
			tup.append((obs['role'], obs['strategy'],obs['payoff']))
		profileData.append(tup)

	res = {
		'roles':roles,
		'players':players,
		'strategies':strategies,
		'profileData':profileData
	}

	# pprint.pprint(roles)
	# pprint.pprint(players)
	# pprint.pprint(strategies)
	# pprint.pprint(profileData)

	return res

if __name__=='__main__':
	r = makeData(sys.argv[1])
	g = Game.Game(r['roles'], r['players'], r['strategies'], r['profileData'], 0)
	g.reduceGame()
	# pprint.pprint(g.findCliques())
	g.solveGames()
