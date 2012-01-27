from blargh import Blargh
from math import pi
import random

# Behavior-related constants.
BACKUP_TIME = 2
TURN_TIME = 2
BALL_CAPTURE_THRESHOLD = 3
THETA_THRESHOLD = pi / 6
AQUIRE_TIME = 3

STATE_CHANGE_FLAG = 0

# Will, this is a hack, change it when you rewrite plzzzzz (unless you want
# me to, cuz I can) kthx
# -Tej
class World():
    def __init__(self, balls, bumpData, irData, time, wallInFront):
        self.balls = balls
        self.bumpData = bumpData
        self.irData = irData
        self.time = time
        self.wallInFront = wallInFront
    def isWallInFront(self):
        return self.wallInFront

world = World([], None, None, 0, False)

class State(object):
    def step(self):
        if world.time > 179:
            print "World.time", world.time, " is too high"
            return DeadState(), STATE_CHANGE_FLAG
        if world.isWallInFront() or ( not world.bumpData == None and (world.bumpData.left or world.bumpData.right)):
            return EscapeState(), STATE_CHANGE_FLAG
        else:
            return None,None      
    

class EscapeState( State ):
    def __init__( self ):
        self.startTime = world.time
    def step( self ):         
        #stepArgs = super(EscapeState, self).step()
        #if (stepArgs[1] == STATE_CHANGE_FLAG):
        #    return stepArgs

        if ( world.time - self.startTime < BACKUP_TIME ):
            goal = ( -20, 0 )
        else:
            goal = (0, pi / 4)

        #If we've hit the timeout, switch to driving straight.
        if ( world.time - self.startTime > BACKUP_TIME + TURN_TIME ):
            return DriveStraightState(), STATE_CHANGE_FLAG
        #Otherwise, keep turning.
        else:
            return self, goal

class DriveStraightState( State ):
    def __init__( self ):
         self.lastTime = world.time

    def step( self ):
        stepArgs = super(DriveStraightState,self).step()
        if (stepArgs[1] == STATE_CHANGE_FLAG):
            #print "Using super"
            return stepArgs
        
        goal = ( 20, 0 )
        print "Drive Straight State"
        #If we see a ball...
        if not world.balls == None and len( world.balls ) > 0 :
            print "See Ball"
            return SeekBallState(), STATE_CHANGE_FLAG

        #With 0.50 chance per second, switch to turning.
        randomval = random.random()
        if random.random() < 1 - ( 1 - 0.20 )**(world.time - self.lastTime):
            print "should turn"
            return TurnState(), STATE_CHANGE_FLAG

        # Otherwise, full steam ahead.
        else:
            self.lastTime = world.time
            return self, goal

class TurnState( State ):
    def __init__( self ):
         self.lastTime = world.time

    def step( self ):
        stepArgs = super(TurnState,self).step()
        if(stepArgs[1] == STATE_CHANGE_FLAG):
            return stepArgs

        goal = ( 0, pi / 16 )
        #If we see a ball...
        if not world.balls == None and len( world.balls ) > 0 :
                return SeekBallState(), STATE_CHANGE_FLAG

        #With 0.10 chance per second, switch to driving forward.
        if random.random() < 1 - ( 1 - 0.50 )**(world.time - self.lastTime):
            return DriveStraightState(), STATE_CHANGE_FLAG

        #Otherwise, turn.
        else:
            self.lastTime = world.time
            return self, goal

class SeekBallState( State ):
    def step( self ):
        print "In seek ball"
        stepArgs = super(SeekBallState,self).step()
        if (stepArgs[1] == STATE_CHANGE_FLAG):
            return stepArgs

        #If we've lost sight of all balls, go back to driving around.
        if world.balls == None or len( world.balls ) == 0 :
            return DriveStraightState(), STATE_CHANGE_FLAG
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
                return AquireBallState(), STATE_CHANGE_FLAG
            #Otherwise, keep seeking.
            else:
                return self, closestBall

class AquireBallState( State ):
    def __init__( self ):
        self.startTime = world.time

    def step( self ):
        stepArgs = super(AquireBallState,self).step()
        if(stepArgs[1] == STATE_CHANGE_FLAG):
            return stepArgs

        goal = ( 10, 0 )
        #If we've hit the timeout, switch to driving straight.
        if ( world.time - self.startTime > AQUIRE_TIME ):
            return DriveStraightState(), STATE_CHANGE_FLAG

        #Otherwise, full steam ahead.
        else:
            self.lastTime = world.time
            return self, goal

class DeadState( State ):    
    # Don't do anything from now on. Once you reach DeadState, you stay there and don't move.
    def step( self ):
        return self, ( 0,0 ) # "Haha, it looks like an owl" -- The Great Ryan Andrew Cheu


class StateMachine:

    def __init__( self, firstState ):
        self.state = firstState
        self.goal = STATE_CHANGE_FLAG

    def step( self ):
        print "State:",self.state
        stateReturns = self.state.step()
        if (not stateReturns == None ):
            self.state, self.goal = stateReturns
        else:
            print "state none return",self.state

        
# Takes in the state of the world and puts out some behavior based on
# previous state (BehaviorBlargh is also a state machine :P)
class BehaviorBlargh(Blargh):

    def __init__(self):
        # Set up the State Machine.
        self.StateMachine = StateMachine( DriveStraightState() )

    def step(self, new_world):
        global world
        world = new_world

        # Act on the model of the world if we have one. Otherwise, return None.
        if not world.balls == None:
            print "balls:", world.balls
        self.StateMachine.step()
        return self.StateMachine.goal
