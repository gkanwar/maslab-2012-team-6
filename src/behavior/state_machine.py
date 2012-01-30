from state import *

class StateMachine:

    def __init__( self, firstState ):
        self.state = firstState
        self.goal = STATE_CHANGE_FLAG

    def step(self, world):
        newState, goal = self.state.step(world)
        if newState != self.state:
            print "State is", self.state
        self.state, self.goal = newState, goal
