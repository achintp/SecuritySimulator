import sys
import json
import pprint
import numpy as np
import pylab as pl
from mpl_toolkits.mplot3d import Axes3D

def plotFromProfiles(profileData):
	"""
		Input needs to be profile data
		List of list containing two tuples
		(role, strategy, value)
	"""
	labels = [[],[]]
	payoffs = {}
	for item in profileData:
		for i,tup in enumerate(item):
			if tup[0] in payoffs.keys():
				payoffs[tup[0]].append(tup[2])
			else:
				payoffs[tup[0]] = [tup[2]]
			labels[i].append(tup[1])

	# pprint.pprint(labels)
	# pprint.pprint(payoffs)

	dummies = []
	for item in labels:
		t =  []
		prev = None
		counter = 1
		for i in item:
			if prev == None:
				prev = i
				t.append(counter)
			else:
				if i == prev:
					t.append(counter)
				else:
					counter += 1
					t.append(counter)
					prev = i
		dummies.append(t)

	print dummies	

	for k,v in payoffs.iteritems():
		fig = pl.figure()
		ax = Axes3D(fig)
		ax.scatter3D(dummies[0], dummies[1], v)
		ax.set_xticklabels(labels[0])
		ax.set_yticklabels(labels[1])
		pl.show()


def parseArgs(fname):
	with open(fname, 'r') as jFile:
		data = json.load(jFile)

	profileData = []
	for profiles in data['profiles']:
		tup = []
		for obs in profiles['symmetry_groups']:
			tup.append((obs['role'], obs['strategy'],obs['payoff']))
		profileData.append(tup)

	return profileData

if __name__ == '__main__':

	p = parseArgs(sys.argv[1])
	plotFromProfiles(p)