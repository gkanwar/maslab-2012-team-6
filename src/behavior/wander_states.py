from state import *

#TODO remove

from collect_states import *

class DriveStraightState(State):
    GOAL = (20, 0)

    def __init__(self, world):
        if world != None:
            self.lastTime = world.time
        else:
            self.lastTime = 0

    def step(self, world):
        stepArgs = super(DriveStraightState, self).step(world)
        if (stepArgs[1] == STATE_CHANGE_FLAG):
            return stepArgs
        
        goal = DriveStraightState.GOAL

        #If we see a ball...
        if not world.balls == None and len( world.balls ) > 0 :
            return SeekBallState(world), STATE_CHANGE_FLAG

        #With 0.50 chance per second, switch to turning.
        randomval = random.random()
        if random.random() < 1 - ( 1 - 0.20 )**(world.time - self.lastTime):
            return TurnState(world), STATE_CHANGE_FLAG

        # Otherwise, full steam ahead.
        else:
            self.lastTime = world.time
            return self, goal

class TurnState( State ):

    GOAL = (0, pi/16)

    def __init__(self, world):
         self.lastTime = world.time

    def step(self, world):
        stepArgs = super(TurnState,self).step(world)
        if(stepArgs[1] == STATE_CHANGE_FLAG):
            return stepArgs

        goal = TurnState.GOAL
        #If we see a ball...
        if not world.balls == None and len( world.balls ) > 0 :
                return SeekBallState(world), STATE_CHANGE_FLAG

        #With 0.10 chance per second, switch to driving forward.
        if random.random() < 1 - ( 1 - 0.50 )**(world.time - self.lastTime):
            return DriveStraightState(world), STATE_CHANGE_FLAG

        #Otherwise, turn.
        else:
            self.lastTime = world.time
            return self, goal
