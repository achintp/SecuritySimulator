import unittest

import StateClasses
import AgentClasses
import Strategies

class ClassTests(unittest.TestCase):

	def test_states(self):
		q = {'debug':1, 'ResourceList':['a','b','c']}
		s = StateClasses.State(**q)
		names = ['a']
		print (s.getResource(*names)['a']).report()

		self.assertTrue(1)

	def test_agents(self):
		l = {
			'name':'a',
			'strategy':'periodic',
			'resourceList':['b','c','f'],
			'time':5
			}

		a = AgentClasses.Attacker(**l)
		q = {
			'b':{'Probes Till Now':4, 'prob':0.4},
			'c':{'Probes Till Now':6, 'prob':0.3},
			'f':{'Probes Till Now':1, 'prob':0.7},
			'time':7
			}

		a.updateInformation(q)
		act = a.getAction()
		print "Act is\n"
		print act
		print act[1][1]
		print 'Finish\n\n'
		self.assertTrue(1)


if __name__=='__main__':
	unittest.main()