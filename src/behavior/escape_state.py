from math import pi
from state import *

# If this is getting called, we're in some sort of bind. Try and get us out of it.
class EscapeState(State):
    # Constants
    BACKUP_TIME = 2
    TURN_TIME = 2
    BACKUP_GOAL = (-20, 0)
    TURN_GOAL = (0, pi/4)

    def __init__(self, worldWrapper):
        # Keep track of time to go through a few different time-based motions
        self.startTime = worldWrapper.time

    def step(self, worldWrapper):
        # Check global conditions
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # Set our goal based on time
        if (world.time - self.startTime < BACKUP_TIME):
            goal = EscapeState.BACKUP_GOAL
        else:
            goal = EscapeState.TURN_GOAL

        # If we've hit the timeout, switch to driving straight.
        if (world.time - self.startTime > BACKUP_TIME + TURN_TIME):
            return FindBallState(world), STATE_CHANGE_FLAG
        # Otherwise, keep moving
        else:
            return self, goal
