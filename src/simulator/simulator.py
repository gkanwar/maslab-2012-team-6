import pygame
import math
from math import pi, sin, cos, sqrt, atan2
import time
import random

# Constants
# Scale everything by this constant factor when drawing.
PIXELS_PER_INCH = 3
# Robot constraints
ROBOT_RADIUS = 7
BALL_PICKUP_DISTANCE = 5.5

#Camera constraints
CAMERA_MAX_SIGHTING_ANGLE = pi / 6
CAMERA_MIN_SIGHTING_DISTANCE = 10


# Helper function to convert a point in x, y space to r, theta space
def toPolar(x, y):
    r = sqrt(x**2 + y**2)
    angle = atan2(y, x)
    return (r, angle)

# Actually handles simulating all the objects and the robot
class Simulator:
    def __init__(self):
        # Initialize variables
        self.xSize =300
        self.ySize = 170

        self.robot = Robot((self.xSize / 2 , self.ySize / 2))
        self.balls = [Ball((random.randint(0, self.xSize),
                            random.randint(0, self.ySize)),
                            self.robot)
                      for i in range(14)]
        
        self.objects = []
        self.objects.extend(self.balls)
        self.objects.append(self.robot)
        self.objects.extend( makeWalls( [ (50,40), (90,100), (20,40) ] ) )

        # Initialize pygame for visualization
        pygame.init()
        self.screen = pygame.display.set_mode((PIXELS_PER_INCH * self.xSize,
                                               PIXELS_PER_INCH * self.ySize))

    def draw(self):
        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Draw each object
        for obj in self.objects:
            obj.draw(self.screen)

        # Flip the buffers (display everything)
        pygame.display.flip()

    def step(self):
        # Step all the objects...
        for ball in self.balls:
            ball.step()
        self.robot.step()

    # TODO: Reorganize so that this can go with robot
    # Simulates camera vision
    def getBallsDetected(self):
        return self.robot.camera.detectBalls(self.balls)


class Object:
    '''Basic Object Class.'''
    def __init__(self, position):
        self.x, self.y = position

    def setPosition(self, position):
        """ Set the x, y coords of the robot. """
        self.x, self.y = position

    def step(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

class Component:
    # Takes a refrence to the robot of which this is a part.
    def __init__( self, robot ):
        self.robot = robot
        # Make sure we fill up our position, etc.
        self.step()

    def step( self ):
        self.position = self.robot.position
        self.heading = self.robot.heading
        
#Encapsulates Camera functionality for nice code later
class Camera( Component ):
    def __init__( self, robot, maxSightingAngle, minSightingDistance ):
        self.robot = robot
        self.maxSightingAngle = maxSightingAngle
        self.minSightingDistance = minSightingDistance

        self.step()

    # Takes an ( x, y ) position and returns true if that position can be seen by the camera.
    def canSeePosition( self, position ):
        x, y = position
        r, theta = toPolar(y - self.position[1], x - self.position[0])
        theta = self.heading - theta
        # Make sure theta is between -pi and pi
        while theta > pi:
            theta += -2 * pi
        while theta < -1 * pi:
            theta += 2 * pi
        # Returns True if the position is in the vision cone.
        return ( abs(theta) < self.maxSightingAngle and r > self.minSightingDistance )

    def detectBalls(self, balls):
        self.sightedBalls = []
        for ball in balls:
            # Find the theta of the of the ball with respect to the polar
            # coordante system centered on the robot.
            x, y = self.position
            r, theta = toPolar(ball.y - y, ball.x - x)
            theta = self.heading - theta
            
            # If
            # (a) the camera is pointing at the ball
            # (b) the ball hasn't been picked up yet.
            # Then we see it!
            if self.canSeePosition( ( ball.x, ball.y ) ) and not ball.isAquired:
                self.sightedBalls.append( ( r, theta ) )
                ball.isSighted = True
            else:
                ball.isSighted = False
        return self.sightedBalls


class Robot(Object):
    """
    Simulates the physical robot. The robot should be implemented in such a
    way that it can interface with code in the same way as the Arduino
    wrapper(s) and vision module.
    """
    def __init__(self, position):
        # Initialize position
        self.position = position

        # Initialize radius
        self.radius = ROBOT_RADIUS
        # Set the time, to calculate times between steps
        self.lastTime = time.time()

        # Robot heading in radians
        self.heading = 0

        # Set the maximum motor speed
        self.maxMotorSpeed = 20

        # Set initial motor saturations
        self.leftMotorSaturation = 0
        self.rightMotorSaturation = 0

        # Sensor data
        self.camera = Camera( self, CAMERA_MAX_SIGHTING_ANGLE, CAMERA_MIN_SIGHTING_DISTANCE )
        self.components = [ self.camera ]
        self.sightedBalls = []

    # Update the Robot's position
    def step(self):
        # Get the current time, calculate time between steps
        currentTime = time.time()
        delTime = currentTime - self.lastTime

        x, y = self.position
        # I'm assuming this function gets called pretty often, so I can
        # decouple the motions.
        avgSpeed = self.maxMotorSpeed * (self.leftMotorSaturation + self.rightMotorSaturation) / 2
        x += delTime * avgSpeed * sin(self.heading)
        y += delTime * avgSpeed * cos(self.heading)
        self.position = ( x, y )

        # That's right. Radians, bitches.
        self.heading += self.maxMotorSpeed * delTime * (self.leftMotorSaturation - self.rightMotorSaturation) / (2 * self.radius)
        while self.heading > 2 * pi:
            self.heading += -2 * pi
        while self.heading < 0:
            self.heading += 2 * pi

	    # Update time
        self.lastTime = currentTime
        
        #Step all the components
        for component in self.components:
            component.step()

    # Draw the robot
    def draw(self, screen):
        x, y = self.position
        pygame.draw.circle(screen, (0, 0, 255),
                              (int(PIXELS_PER_INCH * x),
                               int(PIXELS_PER_INCH * y)),
                               int(PIXELS_PER_INCH * self.radius))
        pygame.draw.line(screen, (0, 255, 0),
                              (int(PIXELS_PER_INCH * x),
                               int(PIXELS_PER_INCH * y)),
                              (int(PIXELS_PER_INCH * (x + (self.radius * sin(self.heading)))),
                               int(PIXELS_PER_INCH * (y + (self.radius * cos(self.heading))))))

    # Simulates getting a bump hit
    def getBumpSensorHit(self, bumpSensorNum):
        # TODO: Implement this
        raise NotImplementedError

    # Simulates getting an IR distance
    def getIRSensorDist(self, irSensorNum):
        # TODO: Implement this
        raise NotImplementedError

    # Simulates setting a motor speed
    def setMotorSpeed(self, motorNum, speed):
        if motorNum == 0:
            self.rightMotorSaturation = speed
        elif motorNum == 1:
            self.leftMotorSaturation = speed

    # Simulates setting a servo angle
    def setServoAngle(self, servoNum, angle):
        # TODO: Implement this
        raise NotImplementedError

def makeWalls( points ):
    walls = []
    for i in range( len(points) - 1 ):
        walls.append( Wall( points[i], points[i+1] ) )
    return walls
class Wall(Object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def step(self):
        pass
    def draw( self, screen ):
        pygame.draw.line(screen, (0, 255, 0),
                              (int(PIXELS_PER_INCH * self.start[0]),
                               int(PIXELS_PER_INCH * self.start[1])),
                              (int(PIXELS_PER_INCH * self.end[0]),
                               int(PIXELS_PER_INCH * self.end[1])))
class Ball(Object):
    def __init__(self, position, robot):
        # Initialize the location of the ball
        self.x, self.y = position
        self.robot = robot
        # Designates if the ball has been spotted by the camera this step
        # so coloring can change.
        self.isSighted = False
        self.isAquired = False

    def step(self):
        # See if the robot is close enough to pick the ball up.
        robotx, roboty = self.robot.position
        r, theta = toPolar( self.y - roboty, self.x - robotx )
        if r < BALL_PICKUP_DISTANCE:
            self.isAquired = True

    # Draw the ball to the screen
    def draw(self, screen):
        color = ( 255, 0, 0 )
        if self.isSighted:
            color = ( 255, 255, 0 )
        if self.isAquired:
            color = ( 0, 127, 255 )
        pygame.draw.circle(screen, color,
                             (int(PIXELS_PER_INCH * self.x),
                              int(PIXELS_PER_INCH * self.y)),
                              int(PIXELS_PER_INCH * 0.875))

from blargh import Blargh

# Create our own vision blargh to interface correctly with the simulator
class VisionBlargh(Blargh):
    def __init__(self, simulatorInterface):
        self.simulatorInterface = simulatorInterface

    def step(self, inp):
        return self.simulatorInterface.getBallsDetected()
