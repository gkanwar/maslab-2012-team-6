from state import *
from state_machine import *
from ball_acquisition_states import BallAcquisitionState
from find_ball_states import FindBallState
from util import STATE_CHANGE_FLAG

# CollectState actually contains a state machine
class CollectState(State):

    TIMEOUT = 150

    def __init__(self, worldWrapper):
        # Create the internal state machine
        self.stateMachine = StateMachine(FindBallState(worldWrapper))

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Check globals
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # TODO: Check for Ferrous full

        # Check for the timeout to go into scoring state
        if worldWrapper.time > self.TIMEOUT:
            return ScoreState(worldWrapper)

        # Step the state machine and output this state and our new goal
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal
