from blargh import Blargh
from math import pi
import random

class World:
    def __init__( self, balls, time, wallInFront ):
        self.balls = balls
        print time
        self.time = time
        self.wallInFront = wallInFront
    def isWallInFront( self ):
        return self.wallInFront

world = World( [], 0, False )

# Behavior-related constants.
BACKUP_TIME = 2
TURN_TIME = 2
BALL_CAPTURE_THRESHOLD = 11
THETA_THRESHOLD = pi / 6
AQUIRE_TIME = 2

STATE_CHANGE_FLAG = 0

class State:

    def step( self, time ):
        raise NotImplementedError

class EscapeState( State ):
    
    def __init__( self ):
        self.startTime = world.time
    def step( self ):


        if world. time > 179:
            return DeadState(), STATE_CHANGE_FLAG

        if ( world.time - self.startTime < BACKUP_TIME ):
            goal = ( -1, 0 )
        else:
            goal = (0, pi / 2)

        # Update the state.
        # If we hit a wall, stop what we're doing and escape the wall.
        # This SEEMS redundant, but it keeps us from turning into a situation we can't escape from.
        if world.isWallInFront():
            return EscapeState(), STATE_CHANGE_FLAG
        #If we've hit the timeout, switch to driving straight.
        if ( world.time - self.startTime > BACKUP_TIME + TURN_TIME ):
            return DriveStraightState( time ), STATE_CHANGE_FLAG
        #Otherwise, keep turning.
        else:
            return self, goal

class DriveStraightState( State ):

    def __init__( self ):
         self.lastTime = world.time

    def step( self ):

        if world. time > 179:
            return DeadState(), STATE_CHANGE_FLAG

        goal = ( 1, 0 )
        
        # Update the state.

        # If we hit a wall or random chance of 0.0875 chance per second , stop what we're doing and escape the wall.
        if world.isWallInFront() or random.random < 1 - ( 1 - 0.0875)**(world.time - self.lastTime):
            return EscapeState(), STATE_CHANGE_FLAG

        #If we see a ball...
        elif len( world.balls ) > 0 :
            return SeekBallState(), STATE_CHANGE_FLAG

        #With 0.50 chance per second, switch to turning.
        if random.random() < 1 - ( 1 - 0.50 )**(world.time - self.lastTime):
            return TurnState(), STATE_CHANGE_FLAG

        # Otherwise, full steam ahead.
        else:
            self.lastTime = world.time
            return self, goal

class TurnState( State ):

    def __init__( self ):
         self.lastTime = world.time

    def step( self ):
        
        if world. time > 179:
            return DeadState(), STATE_CHANGE_FLAG

        goal = ( 0, pi / 2 )

        
        # Update the state.

        # If we hit a wall, stop what we're doing and escape the wall.
        if world.isWallInFront():
            return EscapeState(), STATE_CHANGE_FLAG

        #If we see a ball...
        elif len( world.balls ) > 0 :
                return SeekBallState(), STATE_CHANGE_FLAG

        #With 0.10 chance per second, switch to driving forward.
        if random.random() < 1 - ( 1 - 0.10 )**(world.time - self.lastTime):
            return DriveStraightState(), STATE_CHANGE_FLAG

        #Otherwise, turn.
        else:
            self.lastTime = world.time
            return self, goal

class SeekBallState( State ):

    def step( self ):

        if world. time > 179:
            return DeadState(), STATE_CHANGE_FLAG

        #If we hit a wall, stop what we're doing and escape the wall.
        if world.isWallInFront():
            return EscapeState(), STATE_CHANGE_FLAG

        #If we've lost sight of all balls, go back to driving around.
        if len( world.balls ) == 0 :
                return DriveStraightState(), STATE_CHANGE_FLAG

        else:
            closestBall = None
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

        if world. time > 179:
            return DeadState(), STATE_CHANGE_FLAG

        goal = ( 1, 0 )

        
        #Update the state.

        #If we hit a wall, stop what we're doing and escape the wall.
        if world.isWallInFront():
            return EscapeState(), STATE_CHANGE_FLAG
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
        return self, ( 0,0 )
class StateMachine:

    def __init__( self, firstState ):
        self.state = firstState
        self.goal = STATE_CHANGE_FLAG

    def step( self ):
        print "State:",self.state
        self.state, self.goal = self.state.step()

        
# Takes in the state of the world and puts out some behavior based on
# previous state (BehaviorBlargh is also a state machine :P)
class BehaviorBlargh(Blargh):

    def __init__(self):
        # Set up the State Machine.
        self.StateMachine = StateMachine( DriveStraightState() )

    def step(self, new_world):
        global world
	    # If the Blargh has been passed a new version of the world to deal with feed it in.
        if not new_world == None:
		    world = new_world
        # Act on the model of the world if we have one. Otherwise, return None.
        if not world == None:
            self.StateMachine.step()
            return self.StateMachine.goal
        else:
            return None
