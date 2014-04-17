import sys
import json
from pprint import pprint

def JsonToNFG(fname):
	with open(fname) as jFile:
		data = json.load(jFile)

	with open('out.nfg', 'w') as out:
		players = []
		out.write("NFG 1 R " + '"' + data['name'] + '"' + '\n')
		out.write('{ ')
		for role in data['roles']:
			players.append(role)
			out.write('"' + role['name'] + '" ')
		out.write(' }{ ')
		for role in data['roles']:
			for i in range(0, role['count']):
				out.write(str(len(role['strategies'])))
				out.write(" ")
		out.write(' }\n')

		for p2strategy in ((data['roles'])[1])['strategies']:
			for p1strategy in ((data['roles'])[0])['strategies']:
				for groups in data['profiles']:
					if ((groups['symmetry_groups'])[0])['strategy'] == p1strategy \
					and ((groups['symmetry_groups'])[1])['strategy'] == p2strategy:
						# print ((groups['symmetry_groups'])[0])['payoff'], ((groups['symmetry_groups'])[1])['payoff']
						out.write(str(((groups['symmetry_groups'])[0])['payoff']) + " " + \
						str(((groups['symmetry_groups'])[1])['payoff']) + " ")





if __name__ == '__main__':
	JsonToNFG(sys.argv[1])