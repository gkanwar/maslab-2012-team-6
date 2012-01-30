from state import *

#TODO remove
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

BALL_CAPTURE_THRESHOLD = 3
THETA_THRESHOLD = pi / 6
AQUIRE_TIME = 3

class SeekBallState(State):
    def step(self, world):
        stepArgs = super(SeekBallState,self).step(world)
        if (stepArgs[1] == STATE_CHANGE_FLAG):
            return stepArgs

        #If we've lost sight of all balls, go back to driving around.
        if world.balls == None or len( world.balls ) == 0 :
            return DriveStraightState(world), STATE_CHANGE_FLAG
        else:
            closestBall = None
            if not world.balls == None:
                for ball in world.balls:       
                    if closestBall == None:
                        closestBall = ball
                        continue
                    if ball[0] < closestBall[0]:
                        closestBall = ball
            #If the ball is close enough to capture and we're facing the right way, do so.
            if closestBall[0] < BALL_CAPTURE_THRESHOLD and ( closestBall[1] < THETA_THRESHOLD or closestBall[1] > 2 * pi - THETA_THRESHOLD ):
                return AquireBallState(world), STATE_CHANGE_FLAG
            #Otherwise, keep seeking.
            else:
                return self, closestBall

class AquireBallState( State ):

    GOAL = (10, 0)

    def __init__(self, world):
        self.startTime = world.time

    def step(self, world):
        stepArgs = super(AquireBallState,self).step(world)
        if(stepArgs[1] == STATE_CHANGE_FLAG):
            return stepArgs
        goal = AcquireBallState.GOAL
        #If we've hit the timeout, switch to driving straight.
        if ( world.time - self.startTime > AQUIRE_TIME ):
            return DriveStraightState(world), STATE_CHANGE_FLAG

        #Otherwise, full steam ahead.
        else:
            self.lastTime = world.time
            return self, goal
