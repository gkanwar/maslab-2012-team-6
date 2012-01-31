import random
import os
import threading
import time
from math import pi
from exceptions import NotImplementedError

from state_machine import StateMachine
from util import timeEqualizedRandom, STATE_CHANGE_FLAG


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
        # Check nnnnnnfor bump, and go into EscapeState if we aren't already
        if world.isWallInFront() or (not world.bumpData == None and (world.bumpData.left or world.bumpData.right)):
            if not isinstance(self, EscapeState):
                return EscapeState(worldWrapper), STATE_CHANGE_FLAG
        return None,None

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
            return AquireBallState(worldWrapper), STATE_CHANGE_FLAG
        # Otherwise, keep seeking.
        else:
            return self, closestBall

class AquireBallState(State):

    GOAL = (10, 0)

    def __init__(self, worldWrapper):
        # Keep track of time for equalized randomness
        self.startTime = worldWrapper.time

    def step(self, world):
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

class DriveStraightState(State):
    GOAL = (20, 0)

    def __init__(self, worldWrapper):
        # Keep track of the time between randomized checks
        self.lastTime = worldWrapper.time

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Do global checks
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed
        
        # Set our goal
        goal = DriveStraightState.GOAL

        # With 0.50 chance per second, switch to turning.
        # TODO: Check this and tweak it for optimal performance
        if random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.20):
            return TurnState(worldWrapper), STATE_CHANGE_FLAG

        # Otherwise, full steam ahead.
        else:
            self.lastTime = worldWrapper.time
            return self, goal

class TurnState(State):

    GOAL = (0, pi/16)

    def __init__(self, worldWrapper):
        # Keep track of the time between random checks for consistency
        self.lastTime = worldWrapper.time

    def step(self, worldWrapper):
        # Check our global conditions
        newState, changed = self.checkGlobal(worldWrapper)
        if(changed == STATE_CHANGE_FLAG):
            return newState

        # Set the goal location
        goal = TurnState.GOAL
        # With 0.50 chance per second, switch to driving forward.
        # TODO: Check this value and tweak for best performance
        if random.random() < timeEqualizedRandom(self.lastTime, worldWrapper.time, 0.5):
            return DriveStraightState(worldWrapper), STATE_CHANGE_FLAG
        # Otherwise, turn.
        else:
            self.lastTime = worldWrapper.time
            return self, goal

'''class FollowWallState(State):
    def __init__(self,worldWrapper):
        self.lastTime = worldWrapper.time
    def step(self, worldWrapper):
        newState, changed = self.checkGlobal(worldWrapper)
        if (changed == STATE_CHANGE_FLAG):
            return newState
        if not worldWrapper.world.irData == None:
            irData = worldWrapper.world.irData;
            if (irData.left 
'''
            
# Collect state actually contains a state machine
class FindBallState(State):
    def __init__(self, worldWrapper):
        # Create our internal state machine
        self.stateMachine = StateMachine(DriveStraightState(worldWrapper))

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Do the global checks
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # If we see any balls
        if len(world.balls) > 0:
            return BallAcquisitionState(worldWrapper), STATE_CHANGE_FLAG

        # Step the state machine
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal

# CollectState actually contains a state machine
class CollectState(State):

    TIMEOUT = 150

    def __init__(self, worldWrapper):
        # Create the internal state machine
        self.stateMachine = StateMachine(FindBallState(worldWrapper))

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Check globals
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # TODO: Check for Ferrous full

        # Check for the timeout to go into scoring state
        if worldWrapper.time > self.TIMEOUT:
            return ScoreState(worldWrapper)

        # Step the state machine and output this state and our new goal
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal

# CollectState actually contains a state machine
class CollectState(State):

    TIMEOUT = 180

    def __init__(self, worldWrapper):
        # Create the internal state machine
        self.stateMachine = StateMachine(FindBallState(worldWrapper))

    def step(self, worldWrapper):
        world = worldWrapper.world

        # Check globals
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # TODO: Check for Ferrous full

        # Check for the timeout to go into scoring state
        if worldWrapper.time >= self.TIMEOUT:
            #return ScoreState(worldWrapper)
            os.system("pkill mpg123")
            return DeadState(worldWrapper)

        # Step the state machine and output this state and our new goal
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal

# TODO: Flesh this out
class ScoreState(State):
    def __init__(self):
        pass

# If this is getting called, we're in some sort of bind. Try and get us out of it.
class EscapeState(State):
    # Constants
    BACKUP_TIME = 2
    TURN_TIME = 2
    BACKUP_GOAL = (-20, 0)
    TURN_GOAL = (0, pi/4)

    def __init__(self, worldWrapper):
        # Keep track of time to go through a few different time-based motions
        self.startTime = worldWrapper.time

    def step(self, worldWrapper):
        # Check global conditions
        newState, changed = self.checkGlobal(worldWrapper)
        if changed == STATE_CHANGE_FLAG:
            return newState, changed

        # Set our goal based on time
        if (worldWrapper.time - self.startTime < self.BACKUP_TIME):
            goal = EscapeState.BACKUP_GOAL
        else:
            goal = EscapeState.TURN_GOAL

        # If we've hit the timeout, switch to driving straight.
        if (worldWrapper.time - self.startTime > self.BACKUP_TIME + self.TURN_TIME):
            return CollectState(worldWrapper), STATE_CHANGE_FLAG
        # Otherwise, keep moving
        else:
            return self, goal

class MusicPlayer(threading.Thread):
    def run(self):
        os.system("../sounds/terrantheme1.mp3")

# Special state that we start out and end in
class DeadState(State):

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
            return self, 1 # "Haha, it looks like an owl" -- The Great Ryan Andrew Cheu    
