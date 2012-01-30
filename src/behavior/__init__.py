from blargh import Blargh
from states import *


from state_machine import *

# If you're thinking about refactoring this, please don't, or at least talk to either Will or Bianca first. Lots of the code which looks like it can be consolidated has purposely been copy pasted because it'll be branching out soon. Moving it back will just mean we have to copy paste again.
# <3 Will
        
# Takes in the state of the world and puts out some behavior based on
# previous state (BehaviorBlargh is also a state machine :P)
class BehaviorBlargh(Blargh):

    def __init__(self):
        # Set up the State Machine.
        self.StateMachine = StateMachine(DriveStraightState(None))

    def step(self, world):

        # Act on the model of the world if we have one. Otherwise, return None.
        self.StateMachine.step(world)
        return self.StateMachine.goal
