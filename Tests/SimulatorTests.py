import unittest
import StateClasses
import AgentClasses
import Strategies
import Simulator

class SimTests(unittest.TestCase):

	def inputData(self):
		self.params = {
			'startTime':0,
			'endTime':30,
			'ResourceList': ['ServerA', 'ServerB', 'ServerC'],
			'attackerList': {'A':'periodic'},
			'defenderList': {'D':'periodic'}
		}

		self.sim = Simulator.SimulateCyberScenario(self.params)


	def test_SimInit(self):
		self.inputData()
		self.sim = Simulator.SimulateCyberScenario(self.params)
		print "Simulator successfully created"
		print self.sim.attackerList[0].resourceList
		self.assertTrue(self.sim != None)

	def test_askAttacker(self):
		print "Testing updateInformation------------------------------\n\n"
		self.inputData()
		while(self.sim.gameState):
			#print "Updating information--------------------------------\n\n"
			self.sim.updateInformation()
			#print "\n\nAsking for actions------------------------------\n\n"
			self.sim.askAttacker()
			self.sim.askDefender()
			#print "\n\nEvent Queue---------------------------------------------\n\n"
			print self.sim.eventQueue
			self.sim.executeAction()

		print self.sim.state.stateHistory
		
		self.assertTrue(1)

if __name__=='__main__':
	unittest.main()
