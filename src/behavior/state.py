import random
from math import pi
STATE_CHANGE_FLAG = 0

class State(object):
    def __init__(self, world):
        pass
    # General state change stuff that should happen in most states
    def step(self, world):
        # Check for time running out
        if world.time > 179:
            return DeadState(), STATE_CHANGE_FLAG
        # Check for bump, and go into EscapeState if we aren't already
        if world.isWallInFront() or ( not world.bumpData == None and (world.bumpData.left or world.bumpData.right)):
            if not isinstance(self, EscapeState):
                return EscapeState(world), STATE_CHANGE_FLAG
        else:
            return None,None

class DeadState( State ):
    # Don't do anything from now on. Once you reach DeadState, you stay there and don't move.
    def step(self, world):
        return self, ( 0,0 ) # "Haha, it looks like an owl" -- The Great Ryan Andrew Cheu    
