from math import pi
import random

# Behavior-related constants.
BACKUP_TIME = 2
TURN_TIME = 2

from state import *
from state_machine import *

# If this is getting called, we're in some sort of bind. Try and get us out of it.
class EscapeState(State):
    # Constants
    BACKUP_GOAL = (-20, 0)
    TURN_GOAL = (0, pi/4)

    def __init__(self, world):
        self.startTime = world.time

    def step(self, world):    
        if (world.time - self.startTime < BACKUP_TIME):
            goal = EscapeState.BACKUP_GOAL
        else:
            goal = EscapeState.TURN_GOAL

        #If we've hit the timeout, switch to driving straight.
        if (world.time - self.startTime > BACKUP_TIME + TURN_TIME):
            return DriveStraightState(world), STATE_CHANGE_FLAG
        #Otherwise, keep turning.
        else:
            return self, goal

# We don't have anything better to be doing, so putz around until something happens.
from wander_states import *
class WanderState(State):
    def __init__(self, world):
        self.stateMachine = StateMachine( DriveStraightState( world ) )

    def step(self, world):
        self.stateMachine.step( world )
        return self, self.stateMachine.goal

from collect_states import *

class CollectState(State):
    def __init__(self, world):
        self.stateMachine = StateMachine( DriveStraightState( world ) )

    def step(self, world):
        self.stateMachine.step( world )
        return self, self.stateMachine.goal

class ScoreState(State):
    def __init__(self, world):
        self.stateMachine = StateMachine( DriveStraightState( world ) )

    def step(self, world):
        self.stateMachine.step( world )
        return self, self.stateMachine.goal
