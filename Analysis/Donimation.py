import copy
import sys
import Game
import pprint
import itertools

def bimatrixDomination(payoff_mat, m, n, debug=0):
	"""
		Based off the paper "A note on strategy elimination
		in bimatrix games-Knuth, Papadimmitriou, Tsitsiklis

		payoff_mat should be a list of lists, containing
		addresable pair of payoff values
	"""
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
				print "@"+str(pairs[1])+str(pairs[0])
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

def findZeroEntry(mat, strats, dim):
	for i in strats:
		for j in strats:
			if i != j:
				if mat[i][j] == 0:
					writeToFile(i,j,dim)
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

def writeToFile(i,j, dim):
	with open('IteratedElim.txt', 'a') as outFile:
		if not dim:
			outFile.write("Row " + str(j) + " dominates row " + str(i) +"\n")
		else:
			outFile.write("Col " + str(j) + " dominates col " + str(i) +"\n")

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
