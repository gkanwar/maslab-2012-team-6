import random
from math import pi
from exceptions import NotImplementedError

STATE_CHANGE_FLAG = 0

class State(object):

    # Define a constructor that takes in a world, subclasses might
    # override this to do what they want to
    def __init__(self, worldWrapper):
        pass

    # General state change stuff that should happen in most states
    def step(self, worldWrapper):
        raise NotImplementedError

    def checkGlobal(self, worldWrapper):
        world = worldWrapper.world
        # Check for time running out
        if worldWrapper.time > 179:
            return DeadState(world), STATE_CHANGE_FLAG
        # Check for bump, and go into EscapeState if we aren't already
        if world.isWallInFront() or (not world.bumpData == None and (world.bumpData.left or world.bumpData.right)):
            if not isinstance(self, EscapeState):
                return EscapeState(worldWrapper), STATE_CHANGE_FLAG
        else:
            return None,None

# Special state that we start out and end in
class DeadState(State):

    # Don't do anything until button push.
    def step(self, worldWrapper):
        world = worldWrapper.world
        # If the power button has been hit
        if world.bumpData != None and world.bumpData.power == True:
            # Go into wandering
            worldWrapper.resetTime()
            return FindBallState(worldWrapper), STATE_CHANGE_FLAG
        else:
            # Stay in DeadState and output a goal that we're already at, so we don't move
            return self, (0,0) # "Haha, it looks like an owl" -- The Great Ryan Andrew Cheu    
