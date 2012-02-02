import random
import os
import threading
import time
from math import pi
from exceptions import NotImplementedError

from state_machine import StateMachine
from util import timeEqualizedRandom, STATE_CHANGE_FLAG


STATE_CHANGE_FLAG = 0
START_TURN_FERROUS_FLAG = 2
STOP_TURN_FERROUS_FLAG = 3

class State(object):

    # Define a constructor that takes in a world, subclasses might
    # override this to do what they want to
    def __init__(self, worldWrapper):
        pass

    # General state change stuff that should happen in most states
    def step(self, worldWrapper):
        raise NotImplementedError

    def checkGlobal(self, worldWrapper,checkBump = True):
        world = worldWrapper.world
        # Check for time running out
        if worldWrapper.time > 179:
            return DeadState(world), STATE_CHANGE_FLAG
        # Check for bump, and go into EscapeState if we aren't already
        if  checkBump and (world.isWallInFront() or (not world.bumpData == None 
            and (world.bumpData.left or world.bumpData.right))):
            return EscapeState(worldWrapper),STATE_CHANGE_FLAG
        return None,None

    def checkForBalls(self, worldWrapper):
        if False:#len(worldWrapper.world.balls) > 0:
            print "BALLS BALLS!"
            return BallAcquisitionState(worldWrapper), STATE_CHANGE_FLAG
        return None,None
    
    def checkForYellow(self, worldWrapper):
        if worldWrapper.time > 150 and worldWrapper.world.yellowTheta != 100:
            return ScoreState(worldWrapper),STATE_CHANGE_FLAG
        return None, None



class SeekBallState(State):
    BALL_CAPTURE_THRESHOLD = 3
    THETA_THRESHOLD = pi / 6
    AQUIRE_TIME = 3

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Check the global conditions
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # Find the closest ball
        closestBall = None
        for ball in world.balls:       
            # If we don't have a closest ball, set this one to it
            if closestBall == None:
                closestBall = ball
                continue
            # Check distance
            elif ball[0] < closestBall[0]:
                closestBall = ball
        # If the ball is close enough to capture and we're facing the right way, do so.
        if closestBall[0] < self.BALL_CAPTURE_THRESHOLD and (closestBall[1] < self.THETA_THRESHOLD or closestBall[1] > 2 * pi - self.THETA_THRESHOLD):
            return AcquireBallState(worldWrapper), STATE_CHANGE_FLAG
        # Otherwise, keep seeking.
        else:
            return self, closestBall

class AcquireBallState(State):

    GOAL = (10, 0)

    def __init__(self, worldWrapper):
        # Keep track of time for equalized randomness
        self.startTime = worldWrapper.time

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Check global conditions
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # Set the goal
        goal = AcquireBallState.GOAL
        # Acquire ball state never goes into anything
        return self, goal

# BallAcquisitionState actually contains a state machine
class BallAcquisitionState(State):

    TIMEOUT = 10

    def __init__(self, worldWrapper):
        # Create and keep track of our state machine
        self.stateMachine = StateMachine(SeekBallState(worldWrapper))
        # Keep track of time for a timeout
        self.lastTime = time.time()

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Check globals
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        newState,changed = self.checkForYellow(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # Check for a timeout
        if time.time() - self.lastTime > self.TIMEOUT:
            return EscapeState(worldWrapper), STATE_CHANGE_FLAG

        # Check for having lost all the balls
        if len(world.balls) == 0:
            return FindBallState(worldWrapper), STATE_CHANGE_FLAG

        # TODO: run the Ferrous

        # Otherwise, step the state machine
        oldState = self.stateMachine.state
        self.stateMachine.step(worldWrapper)
        # Update our timer
        if self.stateMachine.state != oldState:
            self.lastTime = time.time()

        # Step the state machine
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal

class DriveToWallState(State):
    TIMEOUT = 50
    GOAL = (20,0)
    GOOD_DIST = 5
    def __init__(self, worldWrapper):
        self.lastTime = worldWrapper.time
        self.startTime = worldWrapper.time
    def step(self, worldWrapper):
        world = worldWrapper.world
        newState,changed = self.checkGlobal(worldWrapper,False)
        if(changed == STATE_CHANGE_FLAG):
            return newState, changed

        newState,changed = self.checkForBalls(worldWrapper)
        if(changed == STATE_CHANGE_FLAG):
            return newState, changed

        newState,changed = self.checkForYellow(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed


        self.lastTime = worldWrapper.time

        if(self.startTime - worldWrapper.time >= self.TIMEOUT):
            return EscapeState(worldWrapper), STATE_CHANGE_FLAG
        if(random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.20)):
            return TurnState(worldWrapper), STATE_CHANGE_FLAG
        if(world.bumpData != None and (world.bumpData.left  or world.bumpData.right)):
            return AlignToWall(worldWrapper), STATE_CHANGE_FLAG
        if(world.irData != None and world.irData.left < self.GOOD_DIST):
            return FollowWallState(worldWrapper), STATE_CHANGE_FLAG

        return self, self.GOAL

class AlignToWall(State):
    BACKUP_TIME = 0.75
    BACKUP_GOAL = (-20, 0)
    TURN_TIME = 1.5
    TURN_GOAL0 = (0, pi/4)
    TURN_GOAL1 = (0, -pi/4)
    GOOD_DIST = 6
    TIMEOUT = 10
    # Threshold for equality between IRs before aligned
    ALIGN_THRESH = 1
    

    def __init__(self, worldWrapper):
        self.lastTime = worldWrapper.time
        self.startTime = worldWrapper.time

    def step(self, worldWrapper):
        world = worldWrapper.world
        
        # Check for Balls
        newState,changed = self.checkForBalls(worldWrapper)
        if(changed == STATE_CHANGE_FLAG):
            return newState, changed

        newState,changed = self.checkForYellow(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed
        
        # Backup
        if(worldWrapper.time - self.startTime < self.BACKUP_TIME):
            newState, changed = self.checkGlobal(worldWrapper, False)
            if(changed == STATE_CHANGE_FLAG):
                return newState, changed
            goal = self.BACKUP_GOAL
        
        # Turn
        else:
            newState, changed = self.checkGlobal(worldWrapper)
            if(changed == STATE_CHANGE_FLAG):                
                return newState, changed

            goal = self.TURN_GOAL0
            if((world.irData != None  and (world.irData.leftFront <= self.GOOD_DIST or world.irData.leftSide <= self.GOOD_DIST) and abs(world.irData.leftFront - world.irData.leftSide) < self.ALIGN_THRESH) and worldWrapper.time - self.startTime > self.TURN_TIME):
                print "Aligned"
                return FollowWallState(worldWrapper), STATE_CHANGE_FLAG

        # Check Timeout
        if(worldWrapper.time - self.startTime > self.TIMEOUT):
            return FollowWallState(worldWrapper), STATE_CHANGE_FLAG
        self.lastTime = worldWrapper.time
        return self, goal
            

class DriveStraightState(State):
    GOAL = (30, 0)

    def __init__(self, worldWrapper):
        # Keep track of the time between randomized checks
        self.lastTime = worldWrapper.time

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Do global checks
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        newState,changed = self.checkForYellow(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed
        
        # Check for Balls
        if len(world.balls) > 0:
            print "Found some balls in drive straight state", world.balls
            return BallAcquisitionState(worldWrapper), STATE_CHANGE_FLAG

        # Set our goal
        goal = DriveStraightState.GOAL

        # With 0.50 chance per second, switch to turning.
        # TODO: Check this and tweak it for optimal performance
        if random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.20):
            return TurnState(worldWrapper), STATE_CHANGE_FLAG
        if random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.99):
            return DriveToWallState(worldWrapper), STATE_CHANGE_FLAG

        # Otherwise, full steam ahead.
        else:
            self.lastTime = worldWrapper.time
            return self, goal

class TurnState(State):

    GOAL = (0, pi/8)

    def __init__(self, worldWrapper):
        # Keep track of the time between random checks for consistency
        self.lastTime = worldWrapper.time

    def step(self, worldWrapper):
        # Check our global conditions
        newState, changed = self.checkGlobal(worldWrapper)
        if(changed == STATE_CHANGE_FLAG):
            return newState, changed
        
        # Check for balls
        newState,changed = self.checkForBalls(worldWrapper)
        if(changed == STATE_CHANGE_FLAG):
            return newState, changed

        # Check for yellow wall, and change states if the time is greater than 150
        newState,changed = self.checkForYellow(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # Set the goal location
        goal = TurnState.GOAL
        # With 0.50 chance per second, switch to driving forward.
        # TODO: Check this value and tweak for best performance
        if random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.5):
            return DriveStraightState(worldWrapper), STATE_CHANGE_FLAG
        if random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.7):
            return DriveToWallState(worldWrapper), STATE_CHANGE_FLAG
        # Otherwise, turn.
        else:
            self.lastTime = worldWrapper.time
            return self, goal

class FollowWallState(State):
    
    STRAIGHT_GOAL = (20, 0)
    TURNING_GOAL_L = (20, -pi/24)
    TURNING_GOAL_R = (20, pi/24)
    TURN_TIME = 1.0
    WALL_FOLLOW_FAR = 10
    WALL_FOLLOW_CLOSE = 6
    WALL_FOLLOW_BREAK = 20


    TURNED_THRESH_RIGHT = 1
    TURNED_THRESH_LEFT = 1
    TURNED_RIGHT = 0
    TURNED_LEFT = 1
    TURNED_STRAIGHT = 2


    def __init__(self,worldWrapper):
        self.lastTime = worldWrapper.time
        self.tooFar = False

    def step(self, worldWrapper):
        # Check for deadness, bump sensors
        newState, changed = self.checkGlobal(worldWrapper,False)
        if (changed == STATE_CHANGE_FLAG):
            return newState, changed
        # Check for balls 
        newState,changed = self.checkForBalls(worldWrapper)
        if(changed == STATE_CHANGE_FLAG):
            return newState, changed

        newState,changed = self.checkForYellow(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed
        
        if(worldWrapper.world.bumpData != None and
           (worldWrapper.world.bumpData.left or
            worldWrapper.world.bumpData.right)):
            return AlignToWall(worldWrapper), STATE_CHANGE_FLAG

        if not worldWrapper.world.irData == None:
            irData = worldWrapper.world.irData
            print irData.leftFront, irData.leftSide
            '''
            if(random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.10)):
                   return TurnState(worldWrapper), STATE_CHANGE_FLAG
            '''

            # Determine which direction we're turned in
            if (irData.leftFront > irData.leftSide + self.TURNED_THRESH_RIGHT):
                print "We're turned right"
                turned = self.TURNED_RIGHT
            elif (irData.leftSide > irData.leftFront + self.TURNED_THRESH_LEFT):
                print "We're turned left"
                turned = self.TURNED_LEFT
            else:
                print "We're turned straight"
                turned = self.TURNED_STRAIGHT

            #BLOCK OF LOGIC
            if(turned == self.TURNED_RIGHT):
                if(irData.leftSide <= self.WALL_FOLLOW_CLOSE):
                    print "Turned right, too close"
                    return self, self.TURNING_GOAL_L
                else:
                    print "Turned right, just fine"
                    return self, self.STRAIGHT_GOAL
            elif(turned == self.TURNED_LEFT):
                if(irData.leftFront >= self.WALL_FOLLOW_FAR):
                    print "Turned left, too far"
                    return self, self.TURNING_GOAL_R
                else:
                    print "Turned left, just fine"
                    return self, self.STRAIGHT_GOAL
            else:
                if(irData.leftSide <= self.WALL_FOLLOW_CLOSE or irData.leftFront <= self.WALL_FOLLOW_CLOSE):
                    print "Straight, too close"
                    return self, self.TURNING_GOAL_R
                elif(irData.leftSide >= self.WALL_FOLLOW_FAR or irData.leftFront >= self.WALL_FOLLOW_FAR):
                    print "Straight, too far"
                    return self, self.TURNING_GOAL_L
                else:
                    print "Straight, just right"
                    return self, self.STRAIGHT_GOAL
            """
            if(irData.left <= self.WALL_FOLLOW_FAR and irData.left >= self.WALL_FOLLOW_CLOSE):
                print "Following wall on the left"
                self.tooFar = False
                return self, self.STRAIGHT_GOAL
            elif(irData.left > self.WALL_FOLLOW_FAR):
                print "Too far on the left"
                if (not self.tooFar):
                    self.tooFar = True
                    self.lastTime = worldWrapper.time
                    return self, self.TURNING_GOAL_L
                elif (worldWrapper.time - self.lastTime > self.TURN_TIME):
                    return self, self.STRAIGHT_GOAL
                else:
                    return self, self.TURNING_GOAL_L
            elif(irData.left < self.WALL_FOLLOW_CLOSE):
                self.tooFar = False
                print "Too close on the left"
                return self, self.TURNING_GOAL_R

#            elif(irData.left > self.WALL_FOLLOW_BREAK and irData.right > self.WALL_FOLLOW_BREAK):
#                print "Breaking away"
#                return DriveStraightState(worldWrapper), STATE_CHANGE_FLAG
            return self, self.STRAIGHT_GOAL

            elif(irData.right<= self.WALL_FOLLOW_FAR and irData.right>= self.WALL_FOLLOW_CLOSE):
                print "Following wall on the right"
                self.wall_followed = 1
                return self, self.STRAIGHT_GOAL
            elif(irData.right > self.WALL_FOLLOW_FAR and irData.right < self.WALL_FOLLOW_BREAK):
                print "Too far on the right"
                return self, self.TURNING_GOAL_R
            elif(irData.right < self.WALL_FOLLOW_CLOSE):
                print "Too close on the right"
                return self, self.TURNING_GOAL_L
"""


# Collect state actually contains a state machine
class FindBallState(State):
    def __init__(self, worldWrapper):
        # Create our internal state machine
        self.stateMachine = StateMachine(DriveStraightState(worldWrapper))

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Do the global checks
        # newState, changed = self.checkGlobal(worldWrapper)
        # if changed == STATE_CHANGE_FLAG:
            # return newState, changed

        # If we see any balls
        # Step the state machine
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal

# TODO: Flesh this out
class ScoreState(State):

    FORWARD_GOAL = 5
    BACKUP_GOAL = 5
    TURN_GOAL = 2
    BACKUP_TIME = 2
    TURN_TIME = 4

    def __init__(self, worldWrapper):
        self.startTime = worldWrapper.time
        self.aligning = False
        self.dumping = False
        self.turnGoal = 0

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Actions
        if self.aligning and worldWrapper.time - self.startTime < self.BACKUP_TIME:
            goal = (self.BACKUP_GOAL, 0)
        elif self.aligning and worldWrapper.time - self.startTime < self.TURN_TIME:
            goal = (self.TURN_GOAL, 0)
        else:
            self.aligning = False
            yellowTheta = world.yellowTheta
            goal = (self.FORWARD_GOAL, yellowTheta)    

        # Fake internal transitions
        if world.bumpData.left and world.bumpData.right:
            goal = (0,TURN_FERROUS_FLAG);
            self.startTime = worldWrapper.time
            self.dumping = True
        elif world.bumpData.left:
            self.startTime = worldWrapper.time
            self.turnGoal = (0,self.TURN_GOAL)
        elif world.bumpData.right:
            self.startTime = worldWrapper.time
            self.turnGoal = (0,-self.TURN_GOAL)
        
        return self, goal

# If this is getting called, we're in some sort of bind. Try and get us out of it.
class EscapeState(State):
    # Constants
    BACKUP_TIME = 1
    TURN_TIME = 1
    BACKUP_GOAL = (-20, 0)
    TURN_GOAL = (0, pi/4)

    def __init__(self, worldWrapper):
        # Keep track of time to go through a few different time-based motions
        self.startTime = worldWrapper.time

    def step(self, worldWrapper):
        # Check global conditions
        newState, changed = self.checkGlobal(worldWrapper,False)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # Set our goal based on time
        if (worldWrapper.time - self.startTime < self.BACKUP_TIME):
            goal = EscapeState.BACKUP_GOAL
        else:
            goalp = EscapeState.TURN_GOAL

        # If we've hit the timeout, switch to driving straight.
        if (worldWrapper.time - self.startTime > self.BACKUP_TIME + self.TURN_TIME):
            return DriveStraightState(worldWrapper), STATE_CHANGE_FLAG
        # Otherwise, keep moving
        else:
            return self, goal

class MusicPlayer(threading.Thread):
    def run(self):
        os.system("mpg123 ../sounds/terrantheme1.mp3")

# Special state that we start out and end in
class DeadState(State):

    DEAD_STATE_FLAG = 1

    # Don't do anything until button push.
    def step(self, worldWrapper):
        world = worldWrapper.world
        # If the power button has been hit
        if world.bumpData != None and world.bumpData.power == True:
            # Go into wandering
            worldWrapper.resetTime()
            MusicPlayer().start()
            return FindBallState(worldWrapper), STATE_CHANGE_FLAG
        else:
            # Stay in DeadState and output a goal that we're already at, so we don't move
            return self, self.DEAD_STATE_FLAG # "Haha, it looks like an owl" -- The Great Ryan Andrew Cheu    
