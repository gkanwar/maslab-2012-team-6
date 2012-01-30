from math import pi
import random

# Behavior-related constants.
BACKUP_TIME = 2
TURN_TIME = 2

from state import *
from state_machine import *


"""
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
"""
