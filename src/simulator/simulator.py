import pygame
import math
from math import pi, sin, cos, sqrt, atan2
import time
import random

from vector import *

# Constants
# Scale everything by this constant factor when drawing.
PIXELS_PER_INCH = 3
# Robot constraints
ROBOT_RADIUS = 7
BALL_PICKUP_DISTANCE = 5.5

# Camera constraints
CAMERA_MAX_SIGHTING_ANGLE = pi / 6
CAMERA_MIN_SIGHTING_DISTANCE = 10
CAMERA_MAX_SIGHTING_DISTANCE = 50


# Converts a vector (x,y) to (r, theta)
def toPolar( v ):
    r = sqrt(v.x**2 + v.y**2)
    theta = atan2(v.y, v.x)
    return (r, theta)

# Converts a point in (r, theta) to (x, y)
def toVector( ( r, theta ) ):
    return scale( r, unitVector( theta ) )

# Actually handles simulating all the objects and the robot
class Simulator:
    def __init__(self):
        # Initialize variables
        self.size = Vector( 300, 170 )

        self.robot = Robot( scale( .5, self.size ) )
        self.balls = [Ball( Vector(random.randint(0, int( self.size.x ) ),
                            random.randint(0, int( self.size.y ) ) ),
                            self.robot)
                      for i in range(12)]
        
        self.objects = []
        self.objects.extend(self.balls)
        self.objects.append(self.robot)
        self.objects.extend( makeWalls( [ Vector(50,40), Vector(30,50), Vector(20,40) ] ) )

        # Initialize pygame for visualization
        pygame.init()
        self.screen = pygame.display.set_mode( ( int( PIXELS_PER_INCH * self.size.x ),
                                               int( PIXELS_PER_INCH * self.size.y ) ) )

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


class Object:
    '''Basic Object Class.'''
    def __init__(self, position):
        self.position = position

    def setPosition(self, position):
        """ Set the position of the object. """
        self.position = position

    def step(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

class Component:
    # Takes a refrence to the robot of which this is a part.
    # offset = offset on the robot in (r, theta) (theta = 0 is the front)
    # headingOffset = Angle the sensor is pointing at in radians.
    def __init__( self, robot, offset, headingOffset ):
        self.robot = robot

        self.offset = offset
        self.headingOffset = headingOffset
        # Make sure we fill up our position, etc.
        self.step()

    def step( self ):
        #Get ( x, y ) offset from the robot.
        r, theta = self.offset
        self.position = self.robot.position + toVector( ( r, theta + self.robot.heading ) )

        self.heading = self.robot.heading + self.headingOffset
    
    # Takes a vector object and returns the local r theta position with respect to the object.
    def localize( self, position ):
        r, theta = toPolar( Vector( position.y - self.position.y, position.x - self.position.x ) )

        #Rotate the point so that theta = 0 means it's right in front of the component.
        theta = theta - self.heading

        # Make sure theta is between -pi and pi
        while theta > pi:
            theta += -2 * pi
        while theta < -1 * pi:
            theta += 2 * pi

        return ( r, theta )
        
#Encapsulates Camera functionality for nice code later
class Camera( Component ):

    # Takes an vector position (in the world) and returns true if that position can be seen by the camera.
    def canSee( self, position ):
        r, theta = self.localize( position )

        # Returns True if the position is in the vision cone.
        return ( abs(theta) < CAMERA_MAX_SIGHTING_ANGLE
            and r > CAMERA_MIN_SIGHTING_DISTANCE
            and r < CAMERA_MAX_SIGHTING_DISTANCE )

    
    def detectBalls(self, balls):
        self.sightedBalls = []
        for ball in balls:         
            # If
            # (a) the camera is pointing at the ball
            # (b) the ball hasn't been picked up yet.
            # Then we see it!
            if self.canSee( ball.position ) and not ball.isAquired:
                r, theta = toPolar( Vector( ball.position.y - self.position.y, ball.position.x - self.position.x ) )
                theta = self.heading - theta
                # Make sure theta is between -pi and pi
                while theta > pi:
                    theta += -2 * pi
                while theta < -1 * pi:
                    theta += 2 * pi

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

        # Sensors
        self.camera = Camera( self, ( 0, 0 ), 0 )
        self.components = [ self.camera ]
        self.sightedBalls = []

    # Update the Robot's position
    def step(self):
        # Get the current time, calculate time between steps
        currentTime = time.time()
        delTime = currentTime - self.lastTime

        # Assuming this function gets called pretty often, it can
        # decouple the motions.
        avgSpeed = self.maxMotorSpeed * (self.leftMotorSaturation + self.rightMotorSaturation) / 2
        self.position = self.position + scale( delTime * avgSpeed, unitVector( self.heading ) )

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
        x, y = self.position.x, self.position.y
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
                              (int(PIXELS_PER_INCH * self.start.x),
                               int(PIXELS_PER_INCH * self.start.y)),
                              (int(PIXELS_PER_INCH * self.end.x),
                               int(PIXELS_PER_INCH * self.end.y)))
class Ball(Object):
    def __init__(self, position, robot):
        # Initialize the location of the ball
        self.position = position
        self.robot = robot
        # Designates if the ball has been spotted by the camera this step
        # so coloring can change.
        self.isSighted = False
        self.isAquired = False

    def step(self):
        # See if the robot is close enough to pick the ball up.
        r, theta = toPolar( self.position - self.robot.position )
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
                             (int(PIXELS_PER_INCH * self.position.x),
                              int(PIXELS_PER_INCH * self.position.y)),
                              int(PIXELS_PER_INCH * 0.875))

from blargh import Blargh

# Create our own vision blargh to interface correctly with the rest of the program
class VisionBlargh(Blargh):
    def __init__(self, simulatorInterface):
        self.simulatorInterface = simulatorInterface

    def step(self, inp):
        return 0, self.simulatorInterface.getBallsDetected()
