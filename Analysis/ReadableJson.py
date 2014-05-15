import sys
import json
import pprint

def JsonToText(fname):
	with open(fname, 'r') as jFile:
		data = json.load(jFile)

	with open('jToT.txt', 'w') as outFile:
		pprint.pprint(data, outFile)

if __name__=='__main__':
	JsonToText(sys.argv[1])