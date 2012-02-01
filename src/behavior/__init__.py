from blargh import Blargh
from state import *

import time

# If you're thinking about refactoring this, please don't, or at least talk to either Will or Bianca first. Lots of the code which looks like it can be consolidated has purposely been copy pasted because it'll be branching out soon. Moving it back will just mean we have to copy paste again.
# <3 Will

# Wrap the world that the World blargh passes in so that we can keep
# track of time correctly
class WorldWrapper():
    def __init__(self):
        self.world = None
        self.startTime = time.time()
        self.time = 0
    def updateWorld(self, world):
        self.world = world
        self.time = time.time() - self.startTime
    def resetTime(self):
        self.startTime = time.time()
        self.time = 0

# Takes in the state of the world and puts out some behavior based on
# previous state (BehaviorBlargh is also a state machine :P)
class BehaviorBlargh(Blargh):

    def __init__(self):
        # Set up the State Machine.
        self.worldWrapper = WorldWrapper()
        self.stateMachine = StateMachine(CollectState(self.worldWrapper))

    def step(self, world):
        # Update the model of the world, then act on it.
        self.worldWrapper.updateWorld(world)
        self.stateMachine.step(self.worldWrapper)
        return self.stateMachine.goal
