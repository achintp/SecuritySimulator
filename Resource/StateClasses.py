import random
import copy
from math import exp

def enum(**enums):
    """Defines enum types. Use by Obj=enum(dict)"""
    return type('Enum', (), enums)

class State(object):
    """Includes all the state information required for the agents to make decisions"""
 
    def __init__(self, *args, **kwargs):
        """
            Pass in dict. Includes:
            ResourceList - list of resource names
        """
        self.debug = 0

        self.currentTime = 0
        self.activeResources = {}
        self.inactiveResources = {}
        self.stateHistory = {}
        self.resourceReportsList = {}

        #Declare and pass the enumeration objects for the players and the server states
        # healthEnum = enum({COMPR=-1, PROBED=0, HEALTHY=1})
        # playerEnum = enum({DEF=0, ATT=1})
        self.rArgs = {'healthState':{}, 'players':{}}
        self.rArgs['alpha'] = kwargs['alpha']
        #Initialize the resources according to the resource list that has been given
        # for name in kwargs['ResourceList']:
        #     self.rArgs['name'] = name
        #     res = Resource(self.rArgs)
        #     res.report()
        #     self.activeResources[name] = res
        self.addResource(kwargs['ResourceList'])
        self.resourceReports()

        if(self.debug):
            for k,v in self.activeResources.iteritems():
                print k + '\n'
                print v.report()

    def addResource(self, args):
        for name in args:
            self.rArgs['name'] = name
            self.activeResources[name] = Resource(self.rArgs)
            self.activeResources[name].report()
        try:
            del self.rArgs['name']
        except KeyError:
            pass

    def resourceReports(self):
        self.resourceReportsList = {}
        for k,v in self.activeResources.iteritems():
            self.resourceReportsList[k] = v.report()
        for k,v in self.inactiveResources.iteritems():
            self.resourceReportsList[k] = v.report()

        if(self.debug):
            print "Resource Reports function:\n"
            for k,v in self.resourceReportsList.iteritems():
                print k
                print v
                print "\n"


    def getResource(self, *args):
        result = {}

        for name in args:
            if self.debug:
                print "getResource name of resource-------------"
                print name 
            t = self.activeResources.get(name)
            #print t
            t = t if t else self.inactiveResources.get(name)
            if(t):
                result[name] = t
        if(self.debug):
            for k,v in result.iteritems():
                print k + '\n'
                print v.report()
        return result

    def recordHistory(self):
        state = {}
        t = {}
        for name, value in self.activeResources.iteritems():
            t[name] = value.report()
        state['activeResources'] = t
        t = {}
        for name, value in self.inactiveResources.iteritems():
            t[name] = value.report()
        state['inactiveResources'] = t
        self.stateHistory[self.currentTime] = state
        if(self.debug):
            "Printing history----------------------------\n\n"
            for name,value in self.stateHistory.iteritems():
                print name, value
            print "--------------------------------------\n\n"

    def updateState(self, time):
        self.updateTime(time)
        self.recordHistory()
        self.resourceReports()

    def updateTime(self, time):
        self.currentTime = time
        

class Resource(object):
    """
        Keeps a track of the server resources being monitored. Initialize by giving enum 
        object of player types and health states in dict
        Initialization: Resource({healthStates:healthEnum, players:playerEnum})
    """
    
    def __init__(self, kwargs):
        self.name = kwargs['name']
        self.stateEnum = kwargs['healthState']
        self.playerEnum = kwargs['players']
        self.probesTillNow = 0
        self.totalProbesTillNow = 0
        self.probCompromise = 0
        self.reimageCount = 0
        self.totalDowntime = 0
        self.Status = "HEALTHY"
        self.controlledBy = "DEF"
        self.alpha = kwargs['alpha']
        self.probeHistory = []
        self.lastReImage = -1
        self.downTime = []

    def report(self):
        # r = copy.deepcopy(self.probeHistory)
        return({"Status":self.Status,
                "Name":self.name,
                "Probes till now":self.probesTillNow,
                "Total Probes till now":self.totalProbesTillNow,
                "Probability of Compromise":self.probCompromise,
                "Reimage Count":self.reimageCount,
                "Total Downtime":self.totalDowntime,
                "Control": self.controlledBy,
                "Probe History": self.probeHistory,
                # "Probe History": r,
                "Last ReImage": self.lastReImage,
                "Downtimes": self.downTime})

    def getStatus(self):
        return(self.Status)

    def changeStatus(self, status):
        if(status == -1):
            self.Status = "COMPR"
        elif(status == 0):
            self.Status = "PROBED"
        elif(status == 1):
            self.Status = "HEALTHY"
        else:
            self.Status = "DOWN"

    # def probe(self):
    #     self.probesTillNow += 1
    #     self.incrementProb()

    # def attack(self):
    #     if(isCompromised()):
    #         self.changeStatus(self.stateEnum.COMPR)
    #         self.controlledBy = self.playerEnum.ATT
    #     else:
    #         self.changeStatus(self.stateEnum.PROBED)

    def incrementProb(self):
        """Increment probability of compromise depending on curve used"""
        #Placholder linear increasing method
        # self.probCompromise += 0.1      
        # if(self.probCompromise>=1):
        #     self.probCompromise = 1
        if(self.probesTillNow < 0):
            self.probCompromise = 0
        else:
            self.probCompromise = (1 - exp(-self.alpha*self.probesTillNow))

    def isCompromised(self):
        #Currently uses a simple random uniform sampling.
        #print "Checking compromise!"
        random.seed()
        rand = random.random()
        if rand<self.probCompromise:
            return 1
        else:
            return 0

    # def reImage(self):
    #     self.probCompromise = 0
    #     self.reimageCount += 1
    #     self.changeStatus(1)

    