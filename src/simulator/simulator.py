import pygame
import math
from math import pi, sin, cos, sqrt, atan, atan2
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

BUMP_SENSOR_THRESHOLD = 0.5


# Converts a vector (x,y) to (r, theta)
def toPolar( v ):
    r = sqrt(v.x**2 + v.y**2)
    theta = atan2(v.y, v.x)
    return (r, theta)

# Converts a point in (r, theta) to (x, y)
def toVector( ( r, theta ) ):
    return scale( r, unitVector( theta ) )

#Returns an equivalent theta from -pi to pi
def normalizeTheta( theta ):
    # Make sure theta is between -pi and pi
    while theta > pi:
        theta += -2 * pi
    while theta < -1 * pi:
        theta += 2 * pi
    return theta
# Actually handles simulating all the objects and the robot
class Simulator:
    def __init__(self):
        # Initialize variables
        self.size = Vector( 300, 170 )

        self.walls = makeWalls( [ Vector(10,10), Vector(290,10), Vector(290,160), Vector( 10, 160 ), Vector( 10, 10 ) ] )+ makeWalls( [ Vector(80,90), Vector(20,30), Vector( 0, 100 ), Vector( 80,90 ) ] ) 
        self.robot = Robot( scale( .5, self.size ), 0, self.walls )
        self.balls = [Ball( Vector(random.randint(0, int( self.size.x ) ),
                            random.randint(0, int( self.size.y ) ) ),
                            self.robot)
                      for i in range(12)]
        self.objects = []
        self.objects.extend(self.balls)
        self.objects.extend(self.walls)
        self.objects.append(self.robot)
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
    def __init__(self, position, heading):
        self.position = position
        self.heading = heading

    def setPosition(self, position):
        """ Set the position of the object. """
        self.position = position

    # Takes a vector position and returns the local r theta position with respect to the object.
    def localize( self, position ):
        r, theta = toPolar(Vector(position.y - self.position.y, position.x - self.position.x))

        #Rotate the point so that theta = 0 means it's right in front of the component.
        theta = normalizeTheta( theta - self.heading )

        return ( r, theta )

    def step(self):
        raise NotImplementedError

    def draw(self, screen):
        raise NotImplementedError

class Component( Object ):
    # Takes a refrence to the robot of which this is a part.
    # offset = offset on the robot in (r, theta) (theta = 0 is the front)
    # headingOffset = Angle the sensor is pointing at in radians.
    def __init__( self, robot, offset, headingOffset ):
        self.robot = robot

        self.offset = offset
        self.headingOffset = headingOffset
        # Make sure we fill up our positipon, etc.
        self.step()

    def step( self ):
        #Get ( x, y ) offset from the robot.
        r, theta = self.offset
        self.position = self.robot.position + toVector( ( r, theta + self.robot.heading ) )

        self.heading = self.robot.heading + self.headingOffset
        
#Encapsulates Camera functionality for nice code later
class Camera( Component ):

    # Takes an vector position (in the world) and returns true if that position can be seen by the camera.
    def canSee( self, other ):
        r, theta = self.localize( other.position )

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
            if self.canSee( ball ) and not ball.isAquired:
                r, theta = self.localize( ball.position )
                # I think that the convention for VisionBlargh is set opposite the direction here... whoops.
                self.sightedBalls.append( ( r, -1 * theta ) )
                ball.isSighted = True
            else:
                ball.isSighted = False
        return self.sightedBalls

class BumpSensor(Component):
    def __init__(self,angle = 0):
        self.val = False
        self.angle = angle
    def isPressed(self):
        return self.val
    def setVal(self,val):
        self.val = val
    def getAngle(self):
        return self.angle
        
        


class Robot(Object):
    """
    Simulates the physical robot. The robot should be implemented in such a
    way that it can interface with code in the same way as the Arduino
    wrapper(s) and vision module.
    """
    def __init__(self, position, heading, walls):
        # Initialize position
        self.position = position
        self.heading = heading
        self.walls = walls

        self.bumpSensors = [BumpSensor(0.5), BumpSensor(-0.5), BumpSensor(pi), BumpSensor(0)]

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

    # Update the Robot's position
    def step(self):
        
        # Get the current time, calculate time between steps
        currentTime = time.time()
        delTime = currentTime - self.lastTime

        # Assuming this function gets called pretty often, it can
        # decouple the motions.

        # Update Position
        avgSpeed = self.maxMotorSpeed * (self.leftMotorSaturation + self.rightMotorSaturation) / 2
        self.position = self.position + scale( delTime * avgSpeed, unitVector( self.heading ) )

        # Update heading
        # That's right. Radians, bitches.
        self.heading = normalizeTheta( self.heading + self.maxMotorSpeed * delTime * (self.leftMotorSaturation - self.rightMotorSaturation) / (4 * self.radius) )

        # Check for and fix collisions. Again, this function assumes a frequent call rate. Othewise, it may just miss this.
        for sensor in self.bumpSensors:
            sensor.setVal(False)

        # TODO: check if wall is actually in area...
        for wall in self.walls:
            local_wall = localize( wall, self )
            r, theta, thetaStart, thetaEnd = local_wall
            overlap = self.radius - r
            # Not the most stringent criteria for collision ever, but it hopefully will do it's job.
            if overlap > 0 and thetaStart < 0 and thetaEnd > 0:
                #Move the robot so that it's tanget to the wall
                ortho = theta + self.heading
                overlap +=  0.01 if overlap > 0 else -0.01
                self.position = self.position - scale(overlap, unitVector(ortho))
                for sensor in self.bumpSensors:
                    if(sensor.getAngle() <= theta + BUMP_SENSOR_THRESHOLD 
                       and sensor.getAngle() >= theta - BUMP_SENSOR_THRESHOLD):
                        sensor.setVal(True)

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
        "getBumpSensorHit", bumpSensorNum
        return self.bumpSensors[bumpSensorNum].isPressed()


    # Simulates getting an IR distance
    def getIRSensorDist(self, irSensorNum):
        smallest = float("inf")
        for wall in self.walls:

            rStart, thetaStart = self.localize( wall.start )
            rEnd, thetaEnd = self.localize( wall.end )
            start = toVector( (rStart, thetaStart) )
            end = toVector( (rEnd, thetaEnd) )

           # Calculate the standard form mx+b
            if (start.x  == end.x):
                m = float("inf")
            m = float( start.y - end.y ) /float( start.x - end.x )
            b = start.y - m * start.x

            x = -b/m

            # print "dist: ",x,b,m,len(self.walls)
            if((x <= end.x and x >= start.x) or (x >= end.x and x <= start.x)):
                if(irSensorNum == 0):
                    if(x < 0  and abs(x) < smallest):
                        smallest = abs(x)
                elif(irSensorNum == 1):
                    if(x > 0 and x < smallest):
                        smallest = x

        return smallest - self.radius

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
def localize( wall, obj ):
    # Find the start and end of the lines in local space (x,y)
    rStart, thetaStart = obj.localize( wall.start )
    rEnd, thetaEnd = obj.localize( wall.end )
    start = toVector( (rStart, thetaStart) )
    end = toVector( (rEnd, thetaEnd) )

    # Calculate the standard form mx+b
    m = float( start.y - end.y ) /float( start.x - end.x )
    b = start.y - m * start.x
    
    # r = x * cos( theta ) + y * sin( theta )
    # b = y - mx
    # Thus assuming b > 0, which we'll cover in a moment ...
    r = b / sqrt( 1 + m ** 2 )
    theta = atan2( (-m*b) / (m**2 + 1), (b) / (m**2 + 1) )
    
    #If r < 0, -r -> r, theta + pi -> theta
    if r < 0:
        r = -1 * r
        theta += pi
    
    theta = normalizeTheta( theta )
    if thetaStart < thetaEnd:
        return(r, theta, thetaStart, thetaEnd)
    return(r, theta, thetaEnd, thetaStart)
    
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
        return 0, (self.simulatorInterface.getBallsDetected(), -1)
