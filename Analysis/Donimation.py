import copy
import sys
import Game
import json
import pprint
import itertools
from tabulate import tabulate

def deltaBimatrixDominationTop(payoffMat, m, n, increment, limit, stratDict, debug=0):
	rowList = [i for i in range(m)]
	colList = [i for i in range(n)]

	mutableStratDict = copy.deepcopy(stratDict)
	# pprint.pprint(mutableStratDict)
	# stratDict['redRows'] = stratDict['ATT']
	# stratDict['redCols'] = stratDict['DEF']
	# stratDict.pop('ATT', None)
	# stratDict.pop('DEF', None)
	# pprint.pprint(stratDict)
	payoff_mat = copy.deepcopy(payoffMat)
	trackDict = {
	'redRows':{i:i for i in rowList},
	'redCols':{i:i for i in colList}
	}
	delta = -increment
	counter = 0
	printTable(mutableStratDict, payoff_mat)

	while 1:
		print "Iteration-" + str(counter)
		print "Game size" + str(m) + 'x' + str(n)
		# pprint.pprint(trackDict)
		# delta = counter*increment
		delta = delta + increment
		res = None
		res = deltaBimatrixDomination(payoff_mat, m, n, delta, mutableStratDict, debug)
		# for k,v in res.iteritems():
		# 	print k,len(v)
		# print "Delta-" + str(delta)
		#Adjust the tracking of original
		mutableStratDict = res['newDict']
		# rem = {
		# 'redRows':[],
		# 'redCols':[]
		# }
		# for k,v in trackDict.iteritems():
		# 	for p,q in v.iteritems():
		# 		if q in res[k]:
		# 			rem[k].append(p)
		# trackDict = {}
		# for k,v in rem.iteritems():
		# 	trackDict[k] = {p:i for i,p in enumerate(v)}
		# m = len(trackDict['redRows'])
		# n = len(trackDict['redCols'])
		m = len(mutableStratDict['ATT'])
		n = len(mutableStratDict['DEF'])
		printTable(mutableStratDict, res['redMat'])

		if m <= limit:
			#Return res object
			#Show the goddamn strategies
			# for k,v in rem.iteritems():
			# 	print k
			# 	for item in v:
			# 		for p,q in stratDict[k].iteritems():
			# 			if item == q:
			# 				print p
			# 	print '\n'
			# strategyMap = {}
			# for k,v in trackDict.iteritems():
			# 	strategyMap[k] = {}
			# 	for p,q in v.iteritems():
			# 		for s, i in stratDict[k].iteritems():
			# 			if i == p:
			# 				strategyMap[k][s] = q
			rem = {
			'ATT':[],
			'DEF':[]
			}

			for k,v in mutableStratDict.iteritems():
				for s,i in v.iteritems():
					rem[k].append(stratDict[k][s])

			rem['redRows'] = rem['ATT']
			rem['redCols'] = rem['DEF']
			rem.pop('ATT', None)
			rem.pop('DEF', None)

			printTable(mutableStratDict, res['redMat'])
			rem['redMat'] = res['redMat']
			print "The final result-" + str(delta)
			# with open('wtf.json','w') as jFile:
			# 	json.dump(rem['redMat'], jFile)
			#Goddamned pass by reference

			# stratDict['ATT'] = stratDict['redRows']
			# stratDict['DEF'] = stratDict['redCols']
			# stratDict.pop('redRows', None)
			# stratDict.pop('redCols', None)
			return rem
		else:
			counter+=1
			payoff_mat = res['redMat']

def printTable(stratDict, payoffTable):
	 print "\n\nPrinting!\n\n"
	 m = len(payoffTable)
	 n = len(payoffTable[0])

	 TableObject = []
	 for i in range(m+1):
	 	t = []
	 	for j in range(n+1):
	 		t.append(None)
	 	TableObject.append(t)

	 TableObject[0][0] = "Attacker Strats"
	 for i in range(len(payoffTable)):
	 	for j in range(len(payoffTable[0])):
	 		for k,v in stratDict['DEF'].iteritems():
	 			if v == j:
	 				TableObject[0][j+1] = k
	 		for k,v in stratDict['ATT'].iteritems():
	 			if v == i:
	 				TableObject[i+1][0] = k
	 		TableObject[i+1][j+1] = str(payoffTable[i][j])

	 print tabulate(TableObject, headers="firstrow")

def deltaBimatrixDomination(payoff_mat, m, n, delta, mStrDict, debug=0):
	"""
		Based off the paper "A note on strategy elimination
		in bimatrix games-Knuth, Papadimmitriou, Tsitsiklis

		payoff_mat should be a list of lists, containing
		addresable pair of payoff values
	"""
	# print "Running Iterated Elimination"
	# print "Delta - " + str(increment*counter)
	# print "payoff"
	# pprint.pprint(payoff_mat)
	# with open('wtf2.json','w') as jFile:
	# 	json.dump(payoff_mat, jFile)
	# with open('wtf.json','r') as jFile:
	# 	t = json.load(jFile)
	# with open('wtf2.json','r') as jFile:
	# 	q = json.load(jFile)
	# if t == q:
	# 	print 'True'
	# else:
	# 	for item in zip(t,q):
	# 		for pair in zip(item[0], item[1]):
	# 			if pair[0] == pair[1]:
	# 				print 'True'
	# 			else:
	# 				print pair
	# 		print 'New row'
	with open('IteratedElim.txt', 'a') as outFile:
		outFile.write("\n\nDelta - " + str(delta) + "\n\n")

	rows = m
	cols = n

	rowList = [i for i in range(rows)]
	colList = [i for i in range(cols)]

	#Construct the R and C matrices
	R = [[0 for i in range(rows)] for j in range(rows)]
	C = [[0 for i in range(cols)] for j in range(cols)]
	if debug:
		print str(rows)+str(cols)
		print "Rowlist"
		pprint.pprint(rowList)
		print"------------\nColList"
		pprint.pprint(colList)
		print"------------\nR"
		pprint.pprint(R)
		print"------------\nC"
		pprint.pprint(C)

	for pairs in itertools.combinations(rowList,2):
		for j in colList:
			if(payoff_mat[pairs[0]][j][0] > \
			payoff_mat[pairs[1]][j][0]+ delta ):
				R[pairs[0]][pairs[1]] += 1
			if(payoff_mat[pairs[0]][j][0] + delta < \
			payoff_mat[pairs[1]][j][0]):
				R[pairs[1]][pairs[0]] += 1

	for pairs in itertools.combinations(colList,2):
		for j in rowList:
			if(payoff_mat[j][pairs[0]][1] > \
			payoff_mat[j][pairs[1]][1] + delta ):
				C[pairs[0]][pairs[1]] += 1
			if(payoff_mat[j][pairs[0]][1] + delta < \
			payoff_mat[j][pairs[1]][1]):
				# print "@"+str(pairs[1])+str(pairs[0])
				C[pairs[1]][pairs[0]] += 1

	# for pairs in itertools.combinations(rowList,2):
	# 	for j in colList:
	# 		if(payoff_mat[pairs[0]][j][0] == None \
	# 		and payoff_mat[pairs[1]][j][0]== None):
	# 			continue
	# 		# if(payoff_mat[pairs[0]][j][0] != None \
	# 		# and payoff_mat[pairs[1]][j][0]!= None):
	# 		if((payoff_mat[pairs[0]][j][0] > \
	# 		payoff_mat[pairs[1]][j][0]+ delta ) or \
	# 		(payoff_mat[pairs[1]][j][0] == None\
	# 		and payoff_mat[pairs[0]][j][0] != None)):
	# 			R[pairs[0]][pairs[1]] += 1
	# 		if((payoff_mat[pairs[0]][j][0] + delta < \
	# 		payoff_mat[pairs[1]][j][0]) or \
	# 		(payoff_mat[pairs[1]][j][0] != None\
	# 		and payoff_mat[pairs[0]][j][0] == None)):
	# 			R[pairs[1]][pairs[0]] += 1

	# for pairs in itertools.combinations(colList,2):
	# 	for j in rowList:
	# 		if(payoff_mat[j][pairs[0]][1] == None \
	# 		and payoff_mat[j][pairs[1]][1] == None):
	# 			continue
	# 		# if(payoff_mat[j][pairs[0]][1] != None \
	# 		# and payoff_mat[j][pairs[1]][1] != None):
	# 		if((payoff_mat[j][pairs[0]][1] > \
	# 		payoff_mat[j][pairs[1]][1] + delta )or \
	# 		(payoff_mat[j][pairs[0]][1] != None \
	# 		and payoff_mat[j][pairs[1]][1] == None)):
	# 			C[pairs[0]][pairs[1]] += 1
	# 		if((payoff_mat[j][pairs[0]][1] + delta < \
	# 		payoff_mat[j][pairs[1]][1]) or \
	# 		(payoff_mat[j][pairs[0]][1] == None \
	# 		and payoff_mat[j][pairs[1]][1] != None)):
	# 			# print "@"+str(pairs[1])+str(pairs[0])
	# 			C[pairs[1]][pairs[0]] += 1

	if debug:
		print"------------\nR"
		pprint.pprint(R)
		print"------------\nC"
		pprint.pprint(C)

	# print "Before loop"
	# for row in R:
	# 	for item in row:
	# 		print item,
	# 	print "\n------------------------------------------------------------------------------"
	# print "\n"
	# for row in C:
	# 	for item in row:
	# 		print item,
	# 	print "\n------------------------------------------------------------------------------"
	# print "\n\n"

	#Do elimination and updating till end condition
	rRows = [i for i in range(rows)]
	cCols = [i for i in range(cols)]
	while(1):
		#Seach C for a zero entry
		# if debug:
		# print "Entered loop"
		# for row in R:
		# 	for item in row:
		# 		print item,
		# 	print "\n------------------------------------------------------------------------------"
		# print "\n"
		# for row in C:
		# 	for item in row:
		# 		print item,
		# 	print "\n------------------------------------------------------------------------------"
		# print "\n\n"
		# pprint.pprint(payoff_mat)
		dim = 0
		delD = findZeroEntry(R, rRows, dim, mStrDict)
		if debug:
			print "Row to be deleted-"+str(delD)
		if delD == None:
			#Search R for zero entry
			dim = 1
			delD = findZeroEntry(C, cCols, dim, mStrDict)
			if debug:
				print "Col to be deleted-"+str(delD)
			if delD == None:
				break
		if debug:
			print delD
		if not dim:
			#Row has to be deleted
			C = dWhittle2(payoff_mat, C, delD, colList, dim, delta)
			if debug:
				pprint.pprint(C)
			if debug:
				print "rowList before deletion-",
				print rowList
			rowList.remove(delD)
			rRows.remove(delD)
		else:
			R = dWhittle2(payoff_mat, R, delD, rowList, dim, delta)
			if debug:
				pprint.pprint(R)
			colList.remove(delD)
			cCols.remove(delD)

	# print "Exited loop"
	# for row in rRows:
	# 	for col in rRows:
	# 		print R[row][col],
	# 	print "\n------------------------------------------------------------------------------"
	# print "\n"
	# for row in cCols:
	# 	for col in cCols:
	# 		print C[row][col],
	# 	print "\n------------------------------------------------------------------------------"
	# print "\n\n"
	# print rowList
	# print colList
	# reducedGame = [[payoff_mat[j][i] for i in colList] \
	# 				for j in rowList]

	reducedGame = []
	#this part
	newDict = {}
	for k,v in mStrDict.iteritems():
		newDict[k] = {}
	#End this part
	for i,i1 in enumerate(rowList):
		for k,v in mStrDict['ATT'].iteritems():
			if v==i1:
				newDict['ATT'][k] = i
		t = []
		for j,j1 in enumerate(colList):
			# print i,i1,j,j1
			for p,q in mStrDict['DEF'].iteritems():
				if q==j1:
					newDict['DEF'][p] = j
			t.append(payoff_mat[i1][j1])
		reducedGame.append(t)

	# pprint.pprint(newDict)

	# for i,i1 in enumerate(rowList): 
	# 	for j,j1 in enumerate(colList):
	# 		if payoff_mat[i1][j1] != reducedGame[i][j]:
	# 			print "AKASJNFBHABSFBHSFBAKFHABSFNFASFNANFU"

	res = {
	'redRows':rowList,
	'redCols':colList,
	'redMat':reducedGame,
	'newDict': newDict
	}

	# if debug:
		# pprint.pprint(reducedGame)
	# pprint.pprint(rowList)
	# pprint.pprint(colList)
	# pprint.pprint(reducedGame)

	return res



def bimatrixDomination(payoff_mat, m, n, debug=0):
	"""
		Based off the paper "A note on strategy elimination
		in bimatrix games-Knuth, Papadimmitriou, Tsitsiklis

		payoff_mat should be a list of lists, containing
		addresable pair of payoff values
	"""
	print "Running Iterated Elimination"
	rows = m
	cols = n

	rowList = [i for i in range(rows)]
	colList = [i for i in range(cols)]

	#Construct the R and C matrices
	R = [[0 for i in range(rows)] for j in range(rows)]
	C = [[0 for i in range(cols)] for j in range(cols)]
	if debug:
		print str(rows)+str(cols)
		print "Rowlist"
		pprint.pprint(rowList)
		print"------------\nColList"
		pprint.pprint(colList)
		print"------------\nR"
		pprint.pprint(R)
		print"------------\nC"
		pprint.pprint(C)

	for pairs in itertools.combinations(rowList,2):
		for j in colList:
			if(payoff_mat[pairs[0]][j][0] == None \
			and payoff_mat[pairs[1]][j][0]== None):
				continue
			# if(payoff_mat[pairs[0]][j][0] != None \
			# and payoff_mat[pairs[1]][j][0]!= None):
			if((payoff_mat[pairs[0]][j][0] > \
			payoff_mat[pairs[1]][j][0]) or \
			(payoff_mat[pairs[1]][j][0] == None\
			and payoff_mat[pairs[0]][j][0] != None)):
				R[pairs[0]][pairs[1]] += 1
			if((payoff_mat[pairs[0]][j][0] < \
			payoff_mat[pairs[1]][j][0]) or \
			(payoff_mat[pairs[1]][j][0] != None\
			and payoff_mat[pairs[0]][j][0] == None)):
				R[pairs[1]][pairs[0]] += 1

	for pairs in itertools.combinations(colList,2):
		for j in rowList:
			if(payoff_mat[j][pairs[0]][1] == None \
			and payoff_mat[j][pairs[1]][1] == None):
				continue
			# if(payoff_mat[j][pairs[0]][1] != None \
			# and payoff_mat[j][pairs[1]][1] != None):
			if((payoff_mat[j][pairs[0]][1] > \
			payoff_mat[j][pairs[1]][1]) or \
			(payoff_mat[j][pairs[0]][1] != None \
			and payoff_mat[j][pairs[1]][1] == None)):
				C[pairs[0]][pairs[1]] += 1
			if((payoff_mat[j][pairs[0]][1] < \
			payoff_mat[j][pairs[1]][1]) or \
			(payoff_mat[j][pairs[0]][1] == None \
			and payoff_mat[j][pairs[1]][1] != None)):
				# print "@"+str(pairs[1])+str(pairs[0])
				C[pairs[1]][pairs[0]] += 1

	if debug:
		print"------------\nR"
		pprint.pprint(R)
		print"------------\nC"
		pprint.pprint(C)

	#Do elimination and updating till end condition
	rRows = [i for i in range(rows)]
	cCols = [i for i in range(cols)]
	while(1):
		#Seach C for a zero entry
		if debug:
			print "Entered loop"
		dim = 0
		delD = findZeroEntry(R, rRows, dim)
		if debug:
			print "Row to be deleted-"+str(delD)
		if delD == None:
			#Search R for zero entry
			dim = 1
			delD = findZeroEntry(C, cCols, dim)
			if debug:
				print "Col to be deleted-"+str(delD)
			if delD == None:
				break
		if debug:
			print delD
		if not dim:
			#Row has to be deleted
			C = whittle(payoff_mat, C, delD, colList, dim)
			if debug:
				pprint.pprint(C)
			if debug:
				print "rowList before deletion-",
				print rowList
			rowList.remove(delD)
			rRows.remove(delD)
		else:
			R = whittle(payoff_mat, R, delD, rowList, dim)
			if debug:
				pprint.pprint(R)
			colList.remove(delD)
			cCols.remove(delD)

	reducedGame = [[payoff_mat[j][i] for i in colList] \
					for j in rowList]

	res = {
	'redRows':rowList,
	'redCols':colList,
	'redMat':reducedGame
	}

	if debug:
		pprint.pprint(reducedGame)
		pprint.pprint(rowList)
		pprint.pprint(colList)

	return res

def findZeroEntry(mat, strats, dim, mStrDict):
	for i in strats:
		for j in strats:
			if i != j:
				# print i,j
				if mat[i][j] == 0:
					writeToFile(i,j,dim, mStrDict)
					return i
	return None

def whittle(payoff_mat, reduceMat, rInd, dList, dim):
	for pairs in itertools.combinations(dList,2):
		if not dim:
			#Means a row is being removed
			# if(payoff_mat[rInd][pairs[0]][1] != None\
			# and payoff_mat[rInd][pairs[1]][1] != None):
			# 	if(payoff_mat[rInd][pairs[0]][1] > \
			# 	payoff_mat[rInd][pairs[1]][1]):
			# 		reduceMat[pairs[0]][pairs[1]] -= 1
			# 	if(payoff_mat[rInd][pairs[0]][1] < \
			# 	payoff_mat[rInd][pairs[1]][1]):
			# 		reduceMat[pairs[1]][pairs[0]] -= 1\
			if(payoff_mat[rInd][pairs[0]][1] == None \
			and payoff_mat[rInd][pairs[1]][1] == None):
				return reduceMat
			if((payoff_mat[rInd][pairs[0]][1] > \
			payoff_mat[rInd][pairs[1]][1]) or \
			(payoff_mat[rInd][pairs[0]][1] != None \
			and payoff_mat[rInd][pairs[1]][1] == None)):
				reduceMat[pairs[0]][pairs[1]] -= 1
			if((payoff_mat[rInd][pairs[0]][1] < \
			payoff_mat[rInd][pairs[1]][1]) or \
			(payoff_mat[rInd][pairs[0]][1] == None \
			and payoff_mat[rInd][pairs[1]][1] != None)):
				reduceMat[pairs[1]][pairs[0]] -= 1

		else:
			#Means a columnn is being removed
			# if(payoff_mat[pairs[0]][rInd][0] != None \
			# and payoff_mat[pairs[1]][rInd][0]!= None):
			# 	if(payoff_mat[pairs[0]][rInd][0] > \
			# 	payoff_mat[pairs[1]][rInd][0]):
			# 		reduceMat[pairs[0]][pairs[1]] -= 1
			# 	if(payoff_mat[pairs[0]][rInd][0] < \
			# 	payoff_mat[pairs[1]][rInd][0]):
			# 		reduceMat[pairs[1]][pairs[0]] -= 1
			if(payoff_mat[pairs[0]][rInd][0] == None \
			and payoff_mat[pairs[1]][rInd][0]== None):
				return reduceMat
			if((payoff_mat[pairs[0]][rInd][0] > \
			payoff_mat[pairs[1]][rInd][0]) or \
			(payoff_mat[pairs[1]][rInd][0] == None\
			and payoff_mat[pairs[0]][rInd][0] != None)):
				reduceMat[pairs[0]][pairs[1]] -= 1
			if((payoff_mat[pairs[0]][rInd][0] < \
			payoff_mat[pairs[1]][rInd][0]) or \
			(payoff_mat[pairs[1]][rInd][0] != None\
			and payoff_mat[pairs[0]][rInd][0] == None)):
				reduceMat[pairs[1]][pairs[0]] -= 1
	return reduceMat

def dWhittle(payoff_mat, reduceMat, rInd, dList, dim, delta):
	for pairs in itertools.combinations(dList,2):
		if not dim:
			#Means a row is being removed
			# if(payoff_mat[rInd][pairs[0]][1] != None\
			# and payoff_mat[rInd][pairs[1]][1] != None):
			# 	if(payoff_mat[rInd][pairs[0]][1] > \
			# 	payoff_mat[rInd][pairs[1]][1]):
			# 		reduceMat[pairs[0]][pairs[1]] -= 1
			# 	if(payoff_mat[rInd][pairs[0]][1] < \
			# 	payoff_mat[rInd][pairs[1]][1]):
			# 		reduceMat[pairs[1]][pairs[0]] -= 1\
			if(payoff_mat[rInd][pairs[0]][1] == None \
			and payoff_mat[rInd][pairs[1]][1] == None):
				return reduceMat
			if((payoff_mat[rInd][pairs[0]][1] > \
			payoff_mat[rInd][pairs[1]][1] + delta ) or \
			(payoff_mat[rInd][pairs[0]][1] != None \
			and payoff_mat[rInd][pairs[1]][1] == None)):
				reduceMat[pairs[0]][pairs[1]] -= 1
			if((payoff_mat[rInd][pairs[0]][1] + delta < \
			payoff_mat[rInd][pairs[1]][1]) or \
			(payoff_mat[rInd][pairs[0]][1] == None \
			and payoff_mat[rInd][pairs[1]][1] != None)):
				reduceMat[pairs[1]][pairs[0]] -= 1
		else:
			#Means a columnn is being removed
			# if(payoff_mat[pairs[0]][rInd][0] != None \
			# and payoff_mat[pairs[1]][rInd][0]!= None):
			# 	if(payoff_mat[pairs[0]][rInd][0] > \
			# 	payoff_mat[pairs[1]][rInd][0]):
			# 		reduceMat[pairs[0]][pairs[1]] -= 1
			# 	if(payoff_mat[pairs[0]][rInd][0] < \
			# 	payoff_mat[pairs[1]][rInd][0]):
			# 		reduceMat[pairs[1]][pairs[0]] -= 1
			if(payoff_mat[pairs[0]][rInd][0] == None \
			and payoff_mat[pairs[1]][rInd][0]== None):
				return reduceMat
			if((payoff_mat[pairs[0]][rInd][0] > \
			payoff_mat[pairs[1]][rInd][0] + delta) or \
			(payoff_mat[pairs[1]][rInd][0] == None\
			and payoff_mat[pairs[0]][rInd][0] != None)):
				reduceMat[pairs[0]][pairs[1]] -= 1
			if((payoff_mat[pairs[0]][rInd][0] + delta < \
			payoff_mat[pairs[1]][rInd][0])  or \
			(payoff_mat[pairs[1]][rInd][0] != None\
			and payoff_mat[pairs[0]][rInd][0] == None)):
				reduceMat[pairs[1]][pairs[0]] -= 1
	return reduceMat

def dWhittle2(payoff_mat, reduceMat, rInd, dList, dim, delta):
	for pairs in itertools.combinations(dList,2):
		if not dim:
			#Means a row is being removed
			if(payoff_mat[rInd][pairs[0]][1] > \
			payoff_mat[rInd][pairs[1]][1] + delta):
				reduceMat[pairs[0]][pairs[1]] -= 1
			if(payoff_mat[rInd][pairs[0]][1] + delta < \
			payoff_mat[rInd][pairs[1]][1]):
				reduceMat[pairs[1]][pairs[0]] -= 1
		else:
			#Means a columnn is being removed
			if(payoff_mat[pairs[0]][rInd][0] > \
			payoff_mat[pairs[1]][rInd][0] + delta):
				reduceMat[pairs[0]][pairs[1]] -= 1
			if(payoff_mat[pairs[0]][rInd][0] + delta < \
			payoff_mat[pairs[1]][rInd][0]):
				reduceMat[pairs[1]][pairs[0]] -= 1
	return reduceMat

def writeToFile(i,j, dim, mStrDict):
	with open('IteratedElim.txt', 'a') as outFile:
		eliminator = None
		eliminatee = None
		if not dim:
			stratToInd = mStrDict['ATT']
			for k,v in stratToInd.iteritems():
				if v == j:
					eliminator = k
				elif v == i:
					eliminatee = k
				else:
					continue
			# outFile.write("Row " + str(j) + " dominates row " + str(i) +"\n")
			outFile.write("Row " + eliminator + " dominates row " + eliminatee +"\n")
		else:
			stratToInd = mStrDict['DEF']
			for k,v in stratToInd.iteritems():
				if v == j:
					eliminator = k
				elif v == i:
					eliminatee = k
				else:
					continue
			# outFile.write("Col " + str(j) + " dominates col " + str(i) +"\n")
			outFile.write("Col " + eliminator + " dominates col " + eliminatee +"\n")

def samplePayoffs():
	m = [
	[(0,2), (3,1), (None,None)],
	[(1,4), (None,None), (4,1)],
	[(2,1), (4,4), (None,None)]
	]

	# pprint.pprint(m)
	return m

if __name__=='__main__':
	payoffMat = samplePayoffs()
	rows = len(payoffMat)
	cols = len(payoffMat[0])
	pprint.pprint(bimatrixDomination(payoffMat, rows, cols, 1))
