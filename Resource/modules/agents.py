import strategies
from knowledge_state import KnowledgeState


class Agent(object):
    """Base class for all agents"""
    def __init__(self, **kwargs):
        """takes dict as argument. Must contain
        strategy
        time
        resourceNames
        alpha
        """
        # Initialization
        st = kwargs["strategy"].split("-")
        self.stName = st[0]
        self.stParam = st[1]

        # Initialize the knowledge model
        self.knowledge = KnowledgeState(kwargs)

    def seeProbe(self, resource):
        """Called by simulator"""

    def seeReimage(self, resource):
        """Called by simulator"""

    def changeStatus(self, resource, status):
        """Called by simulator"""


class Attacker(Agent):
    """Defines the attacker agent. Derives from agent"""
    def __init__(self, **params):
        super(Attacker, self).__init__(**params)
        self.type = "ATT"
        self.setStrategy()

    def setStrategy(self):
        """Assigns the specific strategy to the agent"""
        if hasattr(self, "strategy"):
            a = strategies.AttackerStrategies({})
            self.decideAction = a.getStrategy(self.strategy)

    def getAction(self):
        # It's important that the knowledge be updated before calling
        return self.decideAction(self.knowledge, self.stParam)


class Defender(Agent):
    """Defines the defender agent. Derives from agent"""
    def __init__(self, **params):
        super(Defender, self).__init__(**params)
        self.type = "DEF"
        self.setStrategy()

    def setStrategy(self):
        """Assigns the specific strategy to the agent"""
        if hasattr(self, "strategy"):
            a = strategies.DefenderStrategies({})
            self.decideAction = a.getStrategy(self.strategy)

    def getAction(self):
        # I know that both the agents are the same. Maybe rethink design
        return self.decideAction(self.knowledge, self.stParam)
