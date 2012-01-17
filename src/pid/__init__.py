import math
import time
from blargh import Blargh
from exceptions import ValueError
#from mapper import Map

# Should eventually implement a PID controller
class PIDBlargh(Blargh):

    # States
    TURN_TO_TARGET = 0
    MOVE_TO_TARGET = 1
    SCOUT = 2
    WANDER = 3
    DODGE_WALL_BACK_UP = 4
    DODGE_WALL_TURN = 5
    DODGE_WALL_STRAIGHT = 6
    DODGE_WALL_TURN_BACK = 7

    # Threshold values
    # Theta threshold
    THETA_EPSILON = math.pi / 20
    # Threshold value for linear motion (in terms of grid spaces)
    LINEAR_EPSILON = 2
    # Time constants
    DODGE_WALL_BACK_UP_TIME = 2
    DODGE_WALL_TURN_TIME = 2
    DODGE_WALL_STRAIGHT_TIME = 3
    DODGE_WALL_TURN_BACK_TIME = 2

    def __init__(self, arduinoInterfaceOutputWrapper):
        self.target = None
        self.stateTimer = time.time()
        self.waypoints = [] # Not used right now
        #self.robot = RobotPose()
        self.state = self.SCOUT
        self.aiow = arduinoInterfaceOutputWrapper

    def step(self, inp):
        if (inp != None):
            type, inp = inp
            # If this is vision input
            if (type == "VISION"):
                r, theta = inp
                if (abs(theta) > self.THETA_EPSILON and self.state == self.MOVE_TO_TARGET):
                    self.state = self.TURN_TO_TARGET
                    self.stateTimer = time.time()
                self.target = (r, theta)
            # If this is a location update step
            elif (type == "MAP"):
                # We don't care right now
                pass
            elif (type == "BUMP"):
                # We hit a wall... dodge it!
                pass 
            else:
                raise ValueError

        # Check for no target
        if (self.target == None):
            self.state = self.SCOUT

        # TURN_TO_TARGET
        if (self.state == self.TURN_TO_TARGET):
            self.aiow.setMotorSpeed(0, self.target.theta)
            self.aiow.setMotorSpeed(1, -self.target.theta)
            self.checkStuck()
        # MOVE_TO_TARGET
        elif (self.state == self.MOVE_TO_TARGET):
            self.aiow.setMotorSpeed(0, 100)
            self.aiow.setMotorSpeed(1, 100)
            self.checkStuck()
        # DODGE_WALL_BACK_UP
        elif (self.state == self.DODGE_WALL_BACK_UP):
            self.aiow.setMotorSpeed(0, -50)
            self.aiow.setMotorSpeed(1, -50)
            if (time.time() - self.stateTimer > self.DODGE_WALL_BACK_UP_TIME):
                self.state = self.DODGE_WALL_TURN_TIME
                self.stateTimer = time.time()
        # DODGE_WALL_TURN
        elif (self.state == self.DODGE_WALL_TURN):
            self.aiow.setMotorSpeed(0, 50)
            self.aiow.setMotorSpeed(1, -50)
            if (time.time() - self.stateTimer > self.DODGE_WALL_TURN_TIME):
                self.state = self.DODGE_WALL_STRAIGHT
                self.stateTimer = time.time()
        # DODGE_WALL_STRAIGHT
        elif (self.state == self.DODGE_WALL_STRAIGHT):
            self.aiow.setMotorSpeed(0, 50)
            self.aiow.setMotorSpeed(1, 50)
            if (time.time() - self.stateTimer > self.DODGE_WALL_STRAIGHT_TIME):
                self.state = self.DODGE_WALL_TURN_BACK
                self.stateTimer = time.time()
            self.checkStuck()
        # DODGE_WALL_TURN_BACK
        elif (self.state == self.DODGE_WALL_TURN_BACK):
            self.aiow.setMotorSpeed(0, -50)
            self.aiow.setMotorSpeed(1, 50)
            if (time.time() - self.stateTimer > self.DODGE_WALL_TURN_BACK_TIME):
                self.state = self.TURN_TO_TARGET
                self.stateTimer = time.time()
            
        # SCOUT
        elif (self.state == self.SCOUT):
            self.aiow.setMotorSpeed(0, 50)
            self.aiow.setMotorSpeed(1, -50)
            if (time.time() - self.stateTimer > 10):
                self.state = self.DODGE_WALL_STRAIGHT
                self.stateTimer = time.time()

    def checkStuck(self):
        # Check for stuck
        if (self.target != None and time.time() - self.targetLastModified > 5):
            self.state = self.DODGE_WALL_BACK_UP
            self.stateTimer = time.time()

    ####################### NOT USED IN MOCK 1 #######################
    def checkDTheta(self, target):
            # Get the difference in angles
            dtheta = Map.getAngleBetweenCoords(self.robot.x, self.robot.y, self.target[0], self.target[1]) - robot.theta
            if (dtheta > math.pi):
                dtheta -= 2 * math.pi
            # If the difference is less than some epsilon, we should turn
            abs(dtheta) > self.THETA_EPSILON
        

# Helper class to keep track of the robot's "pose" - the x, y, and theta
# coordinates
class RobotPose():
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta % (2 * math.pi)

    def rotate(self, dtheta):
        self.theta = (self.theta + dtheta) % (2 * math.pi)

    def translate(self, dx, dy):
        self.x += dx
        self.y += dy

    def setAngle(self, theta):
        self.theta = theta

    def setLocation(self, x, y):
        self.x = x
        self.y = y

    def setPose(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta
