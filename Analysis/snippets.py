import os
import sys
import pprint
import json
import csv
from decimal import Decimal
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

toPlotAgainst = [
	# "probeCountTime-1_10",
	# "probeCountTime-2_50",
	# "periodic-0.1",
	# "periodic-20",
	"periodic-",
	"probeCountTime-"
]

markers = [
	"b*",
	"r^",
	"bo",
	"ro",
	"r*",
	"b^"
]

markers1 = [
	"ro",
	"bo",
	"r^",
	"b^",
	"r*",
	"b*"
]

def makePayoffMat(inFile, fname):
	with open(inFile, 'r') as jFile:
		data = json.load(jFile)

	rows = []
	cols = []

	agents = ['ATT', 'DEF']

	c = csv.writer(open(fname, 'w'))
	for role in agents:
		for item in data['roles']:
			if item['name'] == role:
				rows = item['strategies']
			else:
				cols = item['strategies']
		c.writerow([role + " payoffs"] + cols)
		for row in rows:
			print "Searching for row " + row
			p = []
			for col in cols:
				for profile in data['profiles']:
					rightCol = False
					rightRow = False
					payoff = []
					for obs in profile['symmetry_groups']:
						if obs['role'] == role:
							if obs['strategy'] == row:
								rightRow = True
								payoff = obs['payoff']
						else:
							if obs['strategy'] == col:
								rightCol =True
					if rightRow and rightCol:
						p.append(payoff)
			c.writerow([row] + p)
		c.writerow([""])

def getFileNames(folder):
	l = os.listdir(folder)
	t = []
	for item in l:
		t.append(item[11:-5])
	return t

def assignLabel(label):
	if label == 'ACYD1NoOp':
		return 'Int/Low'
	elif label == 'ACYD2NoOp':
		return 'Con/Low'
	elif label == 'ACYD3x':
		return 'Ava/Low'
	elif label == 'ACYD1D':
		return 'Int/High'
	elif label == 'ACYD2D':
			return 'Con/High'
	elif label == 'ACYD3D':
		return 'Ava/High'
	else:
		return 'None'

def makeGraphAgain(fileList):
	FirstGraph = {}
	secondGraph = {}
	with open(fileList, 'r') as names:
		for line in names:
			print 'Iteratiokn-' + line
			fileName = line.strip()
			with open(fileName, 'r') as jFile:
				data = json.load(jFile)

			firstPlot = []
			secondPlot = []
			
			for profile in data['profiles']:
				doIt = False
				val = None
				val2 = {}
				val3 = None
				for obs in profile['symmetry_groups']:
					if obs['role'] == 'DEF':
						if toPlotAgainst[0] in obs['strategy']:
							add = 0
							val = (obs['strategy'], obs['payoff'])
						elif toPlotAgainst[1] in obs['strategy']:
							add = 1
							val = (obs['strategy'], obs['payoff'])
						else:
							add = -1
					if obs['role'] == 'ATT':
						if obs['strategy'] == 'periodic-0.1':
							doIt = True
				if val != None and doIt:
					if add == 0:
						# print val
						firstPlot.append(val)
					if add == 1:
						# print val
						secondPlot.append(val)
			# pprint.pprint(firstPlot)
			# pprint.pprint(secondPlot)
			# print firstPlot[0][0].split('-')[1]
			firstPlot.sort(key = lambda x: 0 if x[0]=='No-Op' else int((x[0]).split('-')[1]))
			# pprint.pprint(firstPlot)
			secondPlot.sort(key = lambda x:1000*int(((x[0]).split('-')[1]).split('_')[0]) + int(((x[0]).split('-')[1]).split('_')[1]))
			FirstGraph[fileName] = firstPlot
			secondGraph[fileName] = secondPlot

	# pprint.pprint(FirstGraph)
	# pprint.pprint(secondGraph)

	X = []
	Y = {}

	for k,v in FirstGraph.iteritems():
		t = []
		for pair in v:
			if pair[0] == 'No-Op':
				if 100 not in X:
					X.append(100)
			else:
				tic = float(pair[0].split('-')[1])
				if tic not in X:
					X.append(tic)
			t.append(pair[1])
		label = (k.split('/')[1]).split('-')[0]
		label = assignLabel(label)
		Y[label] = t
	# pprint.pprint(X)
	# pprint.pprint(Y)

	handles = []
	labs = []

	names = ['Ava/Low','Ava/High','Int/Low','Int/High','Con/Low','Con/High']
	ordered = []
	for item in names:
		ordered.append((item, Y[item]))
	# ordered.sort()
	for item in ordered:
		print item[0]

	fig, ax = plt.subplots()
	for i,k in enumerate(ordered):
		q = ax.plot(X, k[1], markers1[i], label=k[0], markersize=20)
		handles.append(q)
		labs.append(k[0])
	# print labs
	ax.legend(labs,loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True, numpoints=1, prop={'size':37})
	# plt.plot(X,Y1,'rs',label="ProbeCountTime-1_10",X,Y2,'bo', label="ProbeCountTime-2_50")
	plt.xlabel('Defender Periods')
	plt.ylabel('Defender Payoffs')
	# plt.xticks([0, 1,2,3,4, 5])
	# plt.minorticks_off()
	for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
		item.set_fontsize(45)
	plt.show()

	X = []
	Y = {}

	for k,v in secondGraph.iteritems():
		t = []
		indices = []
		for i, pair in enumerate(v):
			if i not in indices:
				indices.append(i)
			if pair[0] not in X:
				duh = pair[0].split('-')[1]
				if duh == '1_10':
					duh = '1_x'
				X.append(duh)
			t.append(pair[1])
		label = (k.split('/')[1]).split('-')[0]
		label = assignLabel(label)
		Y[label] = t

	pprint.pprint(X)
	pprint.pprint(indices)
	pprint.pprint(Y)

	ordered = []
	for item in names:
		ordered.append((item, Y[item]))
	# ordered.sort()
	for item in ordered:
		print item[0]

	labs = []

	fig, ax = plt.subplots()
	for i,k in enumerate(ordered):
		ax.plot(indices, k[1], markers1[i], label=k[0], markersize=20)	
		labs.append(k[0])	
	ax.legend(labs, loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=3, fancybox=True, shadow=True, numpoints=1, prop={'size':37})
	# plt.plot(X,Y1,'rs',label="ProbeCountTime-1_10",X,Y2,'bo', label="ProbeCountTime-2_50")
	plt.xlabel(r'PCP($\pi$_$P$)')
	plt.ylabel('Defender Payoffs')
	# plt.xticks([0, 1,2,3,4, 5])
	# plt.minorticks_off()
	plt.xticks(range(len(indices)), X, rotation='vertical')
	for item in ([ax.title, ax.xaxis.label] + ax.get_xticklabels()):
		item.set_fontsize(30)
	for item in ([ax.title, ax.yaxis.label] + ax.get_yticklabels()):
		item.set_fontsize(45)
	plt.xlim([0,22])

	plt.show()



def makeGraph(fname, results=None):
	with open(fname, 'r') as jFile:
		data = json.load(jFile)

	firstPlot = []
	secondPlot = []
	thirdPlot = []
	fourthPlot = []
	fifthPlot = []
	for profile in data['profiles']:
		add = -1
		val = None
		val2 = None
		val3 = None
		for obs in profile['symmetry_groups']:
			if obs['role'] == 'DEF':
				if obs['strategy'] == toPlotAgainst[0]:
					add = 0
				elif obs['strategy'] == toPlotAgainst[1]:
					add = 1
				else:
					add = -1
			if obs['role'] == 'ATT':
				if 'periodic-' in obs['strategy']:
					val = tuple([obs['strategy'], obs['payoff']])
				if 'purePeriodic-' in obs['strategy']:
					val2 = tuple([obs['strategy'], obs['payoff']])
		if val != None:
			if add == 0:
				# print val
				firstPlot.append(val)
			if add == 1:
				# print val
				secondPlot.append(val)
		if val2 != None:
			if add == 0:
				# print val
				thirdPlot.append(val2)
			if add == 1:
				# print val
				fourthPlot.append(val2)

	for result in results:
		for k,v in result.iteritems():
			if 'DEF!probeCountTime-1_10@probeCountTime-2_50' == k:
				fifthplot = []
				for strat, vals in v.iteritems():
					if 'periodic-' in strat:
						fifthPlot.append(tuple([strat, vals['total']]))
	firstPlot.sort()
	secondPlot.sort()
	# thirdPlot.sort()
	# fourthPlot.sort()
	fifthPlot.sort()
	pprint.pprint(firstPlot)
	pprint.pprint(secondPlot)
	# pprint.pprint(thirdPlot)
	# pprint.pprint(fourthPlot)
	pprint.pprint(fifthPlot)

	# firstPlotR=[]
	# secondPlotR=[]
	# fifthPlotR=[]

	# for item in firstPlot:
	# 	if (item[0].split('-')[1]).split('_')[0] == '1' or\
	# 	(item[0].split('-')[1]).split('_')[1] == '50':
	# 		firstPlotR.append(item)
	# for item in secondPlot:
	# 	if (item[0].split('-')[1]).split('_')[0] == '1' or\
	# 	(item[0].split('-')[1]).split('_')[1] == '50':
	# 		secondPlotR.append(item)
	# for item in fifthPlot:
	# 	if (item[0].split('-')[1]).split('_')[0] == '1' or\
	# 	(item[0].split('-')[1]).split('_')[1] == '50':
	# 		fifthPlotR.append(item)

	# pprint.pprint(firstPlotR)
	# pprint.pprint(secondPlotR)
	# pprint.pprint(fifthPlotR)

	font = {
	'family' : 'normal',
    'weight' : 'bold',
    'size'   : 50
    }

	X = []
	Y1 = []
	Y2 = []
	Y3 = []

	for item in zip(firstPlot, secondPlot):
		# X.append(float((item[0][0].split('-')[1]).split('_')[0]))
		X.append(float(item[0][0].split('-')[1]))
		Y1.append(item[0][1])
		Y2.append(item[1][1])
		print item[0][0], item[1][0]

	Xcheck = []
	for item in zip(firstPlot, fifthPlot):
		# Xcheck.append(float((item[0][0].split('-')[1]).split('_')[0]))
		Xcheck.append(float(item[0][0].split('-')[1]))
		Y3.append(item[1][1])
		print item[0][0], item[1][0]

	print X, Xcheck

	fig, ax = plt.subplots()
	ax.plot(X, Y1, 'ro', label="vs PCP(1,x)", markersize=20)
	ax.plot(X, Y2,'bs', label="vs PCP(2,50)", markersize=20)
	ax.plot(X, Y3, 'g*', label="vs equilibrium mixture", markersize=20)
	# legend = ax.legend(loc='upper right', shadow=True)	
	ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
          ncol=3, fancybox=True, shadow=True, numpoints=1, prop={'size':37})
	# plt.plot(X,Y1,'rs',label="ProbeCountTime-1_10",X,Y2,'bo', label="ProbeCountTime-2_50")
	plt.xlabel('Attacker Periods')
	plt.ylabel('Attacker Payoffs')
	# plt.xticks([0, 1,2,3,4, 5])
	# plt.minorticks_off()
	for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] + ax.get_xticklabels() + ax.get_yticklabels()):
		item.set_fontsize(55)
	plt.show()

def writeCSV(data, fname, payoffMat = None):
	if payoffMat == None:
		c = csv.writer(open(fname, 'w'))
		for equlibrium in data:
			for equ, items in equlibrium.iteritems():
				equ = equ.split('!')
				strats = equ[1].split('@')
				eq = [equ[0]+"------->"] + strats + ['weighted mean']
				c.writerow(eq)			
				for k,v in items.iteritems():
					values = []
					for i in range(len(strats)+1):
						values.append(None)
					for s,vals in v.iteritems():
						if s == 'total':
							values[-1] = vals
						else:
							for i,st in enumerate(strats):
								if s == st:
									values[i] = vals
					c.writerow([k]+values)
			c.writerow(["","",""])
	
def readSummaryFile(fname, outname):
	with open(fname, 'r') as jFile:
		data = json.load(jFile)

	with open(outname, 'w') as outFile:
		pprint.pprint(data, outFile)

def getAnyRegret(gameFile, params, outname):
	with open(gameFile,'r') as jFile:
		data = json.load(jFile)

	results = []
	equilibria = {}
	for item in params:
		output = {}
		for k,v in item.iteritems():
			# output[k] = v
			equStrats = v
			for roles in data['roles']:
				if roles['name'] != k:
					strats = roles['strategies']
			allStrats = {agentStrats:{equStr:None for equStr in equStrats.keys()} for agentStrats in strats}
			# pprint.pprint(allStrats)
			for profile in data['profiles']:
				add = False
				agentsStrat = None
				observation = {}
				for obs in profile['symmetry_groups']:
					if obs['role'] == k:
						if obs['strategy'] in equStrats:
							stratToAdd = obs['strategy']
							add = True
					if obs['role'] != k:
						if obs['strategy'] in strats:
							observation[obs['strategy']] = obs['payoff']						
				if add:
					for m,n in observation.iteritems():
						allStrats[m][stratToAdd] = n

				# attProfile = profile['symmetry_groups'][0]
				# defProfile = profile['symmetry_groups'][1]
			stringKey = k+"!"+'@'.join(map(str, v.keys()))
			output[stringKey] = allStrats
			# pprint.pprint(allStrats)
		results.append(output)
	pprint.pprint(results)

	for pair in zip(params, results):
		for k,v in pair[1].iteritems():
			role = k.split('!')[0]
			for r,s in pair[0].iteritems():
				if r!=role:
					EqStrats = s
			total = 0
			for strat in EqStrats.keys():
				unweighted = 0
				for m,n in v[strat].iteritems():
					print str(pair[0][role][m])+"*"+str(n)
					unweighted += pair[0][role][m]*n
				print "Total="+str(EqStrats[strat])+"*"+str(unweighted)
				total += EqStrats[strat]*unweighted
				print total
			print role, EqStrats
			print total
			for strat, vals in v.iteritems():
				tot = 0
				for p,q in vals.iteritems():
					tot += pair[0][role][p]*q
				vals['total'] = tot
	# pprint.pprint(results)
	# writeCSV(results, "Spreadsheet.csv")
	makeGraph(gameFile, results)

def readJsonFile(jFile):
	with open(jFile, 'r') as inFile:
		params = json.load(inFile)

	getAnyRegret('Input_files/182-summary.json', params, 'example.json')

	pprint.pprint(params)	


def readResultFiles(fname):
	t = {}
	with open(fname, 'r') as damnFile:
		keep = 0
		for line in damnFile:
			line = line.strip()
			if not line:
				continue
			if line[0] == '{':
				regrets = []
				keep = 1
				line = line[1:]
				f = line.split(',')[0]
				f = f.split(':')[1]
			elif line[0] == '"' and line[1] == '}':
				keep = 0
				t[f] = regrets
			else:
				if line and ',' not in line:
					if keep:
						regrets.append(Decimal(line))
	noRegret = {}
	lB = 1e-06
	for k,v in t.iteritems():
		if min(v) < lB:
			noRegret[k] = v

	pprint.pprint(noRegret)
	print len(noRegret)

	results = []
	with open("ResultsCheckACYD3D.txt", 'w') as outFile:
		for f, r in noRegret.iteritems():
			with open(f[1:-1],'r') as jFile:
				data = json.load(jFile)
			for pair in zip(data, r):
				if pair[1] < lB:
					q = [pair[0]['data'],pair[1]]
					if q not in results:
						results.append(q)
						for k,v in pair[0]['data'].iteritems():
							pprint.pprint(k ,outFile)
							pprint.pprint(pair[0]['data'][k], outFile)
						outFile.write("\n\n")
	pprint.pprint(results)

if __name__ == '__main__':
	readResultFiles(sys.argv[1])
	# readJsonFile(sys.argv[1])
	# makeGraph(sys.argv[1])
	# readSummaryFile(sys.argv[1], 'outFile2.txt')
	# makePayoffMat(sys.argv[1], sys.argv[2])
	# makeGraphAgain(sys.argv[1])