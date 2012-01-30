from state import *
from util import timeEqualizedRandom, STATE_CHANGE_FLAG

BALL_CAPTURE_THRESHOLD = 3
THETA_THRESHOLD = pi / 6
AQUIRE_TIME = 3

class SeekBallState(State):
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
        if closestBall[0] < BALL_CAPTURE_THRESHOLD and (closestBall[1] < THETA_THRESHOLD or closestBall[1] > 2 * pi - THETA_THRESHOLD):
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
        # Check globals
        newState, changed = self.checkGlobals(worldWrapper)
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
        newState, changed =  self.stateMachine.step(worldWrapper)
        # Update our timer
        if newState != oldState:
            self.lastTime = time.time()

        # Step the state machine
        self.stateMachine.step(worldWrapper)
        return self, self.stateMachine.goal
