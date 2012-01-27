from blargh import Blargh
from state import *


class StateMachine:

    def __init__( self, firstState ):
        self.state = firstState
        self.goal = STATE_CHANGE_FLAG

    def step(self, world):
        stateReturns = self.state.step(world)
        if stateReturns[0] != self.state:
            print world.time, self.state
        if not stateReturns == None:
            self.state, self.goal = stateReturns
        else:
            print "State none return", self.state

        
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
