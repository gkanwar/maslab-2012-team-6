from blargh import Blargh
from math import pi
import time
import random

world = None

#Behavior-related constants.
BACKUP_TIME = 2
TURN_TIME = 2
BALL_CAPTURE_THRESHOLD = 1.1
THETA_THRESHOLD = pi / 6
AQUIRE_TIME = 2

class State:

    def __init__( self, time ):
        self.startTime = time
        self.lastTime = time

    def step( self, time ):
        raise NotImplementedError

class EscapeState( State ):

    def step( self, time ):
        print 
        if ( time - self.startTime < BACKUP_TIME ):
            goal = ( -1, 0 )
        else:
            goal = ( 0, pi / 2 )

        #Update the state.
        #If we hit a wall, stop what we're doing and escape the wall.
        #This SEEMS redundant, but it keeps us from turning into a situation we can't escape from.
        if world.isWallInFront():
            return EscapeState( time ), ( 0, 0 )
        #If we've hit the timeout, switch to driving straight.
        if ( time - self.startTime > BACKUP_TIME + TURN_TIME ):
            return DriveStraightState( time ), ( 0, 0 )
        #Otherwise, keep turning.
        else:
            self.lastTime = time
            return self, goal

class DriveStraightState( State ):

    def step( self, time ):
        
        goal = ( 1, 0 )
        
        #Update the state.

        #If we hit a wall, stop what we're doing and escape the wall.
        if world.isWallInFront():
            return EscapeState( time ), ( 0, 0 )

        #If we see a ball...
        elif len( world.balls ) > 0 :
            return SeekBallState( time ), ( 0, 0 )

        #With 0.25 chance per second, switch to turning.
        if random.random() < 1 - ( 1 - 0.25 )**(time - self.lastTime):
            return TurnState( time ), ( 0, 0 )

        #Otherwise, full steam ahead.
        else:
            self.lastTime = time
            return self, goal

class TurnState( State ):

    def step( self, time ):
        
        goal = ( 0, pi / 2 )
        
        #Update the state.

        #If we hit a wall, stop what we're doing and escape the wall.
        if world.isWallInFront():
            return EscapeState( time ), ( 0, 0 )

        #If we see a ball...
        elif len( world.balls ) > 0 :
                return SeekBallState( time ), ( 0, 0 )

        #With 0.25 chance per second, switch to driving forward.
        if random.random() < 1 - ( 1 - 0.25 )**(time - self.lastTime):
            return DriveStraightState( time ), ( 0, 0 )

        #Otherwise, turn.
        else:
            self.lastTime = time
            return self, goal

class SeekBallState( State ):

    def step( self, time ):

        #If we hit a wall, stop what we're doing and escape the wall.
        if world.isWallInFront():
            return EscapeState( time ), ( 0, 0 )

        #If we've lost sight of all balls, go back to driving around.
        if len( world.balls ) == 0 :
                return DriveStraightState( time ), ( 0, 0 )

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
                return AquireBallState( time ), ( 0, 0 )
            #Otherwise, keep seeking.
            else:
                return self, closestBall

class AquireBallState( State ):
    def step( self, time ):
        goal = ( 1, 0 )
        
        #Update the state.

        #If we hit a wall, stop what we're doing and escape the wall.
        if world.isWallInFront():
            return EscapeState( time ), ( 0, 0 )
        #If we've hit the timeout, switch to driving straight.
        if ( time - self.startTime > AQUIRE_TIME ):
            return DriveStraightState( time ), ( 0, 0 )

        #Otherwise, full steam ahead.
        else:
            self.lastTime = time
            return self, goal
                
class StateMachine:

    def __init__( self, firstState ):
        self.state = firstState
        self.goal = ( 0, 0 )

    def step( self, time ):
        self.state, self.goal = self.state.step( time )
        
# Takes in the state of the world and puts out some behavior based on
# previous state (BehaviorBlargh is also a state machine :P)
class BehaviorBlargh(Blargh):

    def __init__(self):
        # Set up the State Machine.
        self.StateMachine = StateMachine( DriveStraightState( time.time() ) )

    def step(self, new_world):
        global world
	    #If the Blargh has been passed a new version of the world to deal with feed it in.
        if not new_world == None:
		    world = new_world
        #Act on the model of the world if we have one. Otherwise, return None.
        if not world == None:
            self.StateMachine.step( time.time() )
            return self.StateMachine.goal
        else:
            return None

if __name__ == "__main__":
        #This is kind of a unit test... I don't think it works anymore
        SM = StateMachine( DriveStraightState( time.time() ) )
        for i in range( 100 ):
                SM.step( time.time() )
                time.sleep(0.1)
        world.isWall = True
        SM.step( time.time() )
        world.isWall = False
        world.balls = [ (1, .2), (2,.3) ]
        for i in range( 100 ):
                SM.step( time.time() )
                time.sleep(0.05)
