from state import *
from util import timeEqualizedRandom

class DriveStraightState(State):
    GOAL = (20, 0)

    def __init__(self, worldWrapper):
        # Keep track of the time between randomized checks
        self.lastTime = worldWrapper.time

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Do global checks
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed
        
        # Set our goal
        goal = DriveStraightState.GOAL

        # With 0.50 chance per second, switch to turning.
        # TODO: Check this and tweak it for optimal performance
        if random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.20):
            return TurnState(worldWrapper), STATE_CHANGE_FLAG

        # Otherwise, full steam ahead.
        else:
            self.lastTime = worldWrapper.time
            return self, goal

class TurnState(State):

    GOAL = (0, pi/16)

    def __init__(self, worldWrapper):
        # Keep track of the time between random checks for consistency
        self.lastTime = worldWrapper.time

    def step(self, worldWrapper):
        # Check our global conditions
        newState, changed = self.checkGlobal(worldWrapper)
        if(changed == STATE_CHANGE_FLAG):
            return newState

        # Set the goal location
        goal = TurnState.GOAL
        # With 0.10 chance per second, switch to driving forward.
        # TODO: Check this value and tweak for best performance
        if random.random() < timeEqualizedRandom(self.lastTime, world.time, 0.5):
            return DriveStraightState(worldWrapper), STATE_CHANGE_FLAG

        # Otherwise, turn.
        else:
            self.lastTime = worldWrapper.time
            return self, goal

# Collect state actually contains a state machine
class FindBallState(State):
    def __init__(self, worldWrapper):
        # Create our internal state machine
        self.stateMachine = StateMachine(DriveStraightState(worldWrapper))

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Do the global checks
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # If we see any balls
        if len(world.balls) > 0:
            return BallAcquisitionState(worldWrapper), STATE_CHANGE_FLAG

        # Step the state machine
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal

