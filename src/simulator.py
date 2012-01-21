#Simululator Code.

import pygame
import math
from math import pi, sin, cos, sqrt, atan2
import time
import random

#Converts a point in x, y space to r, theta space
def toPolar( x, y ):
    r = sqrt( x**2 + y**2 )
    angle = atan2( y, x )
    return ( r, angle )

#Because the simulator measures things in inches, and inches are pretty big unit,
#We need to scale everything by this constant factor when drawing.
PIXELS_PER_INCH = 5

ROBOT_RADIUS = 7
ROBOT_MAX_SIGHTING_ANGLE = pi / 6 

class Simulator:
    def __init__(self):
        # Initialize variables

        self.xSize = 200
        self.ySize = 100

        self.robot = Robot( ( self.xSize / 2 , self.ySize / 2 ) )
        self.balls = [ Ball( ( random.randint( 0, self.xSize ), random.randint( 0, self.ySize ) ), self.robot ) for i in range( 5 ) ]
        
        self.objects = []
        self.objects.extend( self.balls  )
        self.objects.append( self.robot )

        # Initialize pygame for visualization
        pygame.init()
        self.screen = pygame.display.set_mode( ( PIXELS_PER_INCH * self.xSize, PIXELS_PER_INCH * self.ySize ) )

    def draw(self):
        #Draw
        # Clear the screen
        self.screen.fill( (0, 0, 0) )

        # Draw each object
        for obj in self.objects:
            obj.draw( self.screen )

        #Flip the buffers (display everything)
        pygame.display.flip()

    def step( self ):
        #Step all the objects...
        for obj in self.objects:
            obj.step()
        self.robot.detectBalls( self.balls )

class Object:
    '''Basic Object Class.'''
    def __init__( self, position ):
        self.x, self.y = position

    def setPosition( self, position ):
        """ Set the x, y coords of the robot. """
        self.x, self.y = position

    def step( self ):
        raise NotImplementedError

    #No invisible objects
    def draw( self, screen ):
        raise NotImplementedError

class Robot( Object ):
    """Simulates the physical robot. The robot should be implemented in such a way that it can interface with code in the same way as the Arduino wrapper(s) and vision module."""
    def __init__( self, position ):
        self.x, self.y = position

        self.radius = ROBOT_RADIUS
        
        self.lastTime = time.time()

        #robot heading in radians
        self.heading = 0

        #motor info
        self.leftMotorSaturation = 0
        self.rightMotorSaturation = 0

        self.maxMotorSpeed = 20

        #Sensor Data
        self.maxSightingAngle = ROBOT_MAX_SIGHTING_ANGLE
        self.sightedBalls = []

    #Update the Robot's position
    def step( self ):
        currentTime = time.time()
        delTime = currentTime - self.lastTime

        #I'm assuming this function gets called pretty often, so I can decouple the motions.
        avgSpeed = self.maxMotorSpeed * ( self.leftMotorSaturation + self.rightMotorSaturation ) / 2
        self.x += delTime * avgSpeed * sin( self.heading )
        self.y += delTime * avgSpeed * cos( self.heading )

        #That's right. Radians, bitches.
        self.heading += self.maxMotorSpeed * delTime * ( self.leftMotorSaturation - self.rightMotorSaturation ) / ( 2 * self.radius )
        while self.heading > 2 * pi:
            self.heading += -2 * pi
        while self.heading < 0:
            self.heading += 2 * pi
        
        self.lastTime = currentTime

    def draw( self, screen ):
        pygame.draw.circle( screen, (0, 0, 255), ( int( PIXELS_PER_INCH * self.x ), int( PIXELS_PER_INCH * self.y ) ), int( PIXELS_PER_INCH * self.radius ) )
        pygame.draw.line( screen, (0, 255, 0), ( int( PIXELS_PER_INCH * self.x ), int( PIXELS_PER_INCH * self.y ) ), ( int( PIXELS_PER_INCH * ( self.x + ( self.radius * sin( self.heading ) ) ) ), int( PIXELS_PER_INCH * ( self.y + ( self.radius * cos( self.heading ) ) ) ) ) )

    def setMotorSpeed( self, motorNum, speed ):
        if motorNum == 0:
            self.leftMotorSaturation = speed
        elif motorNum == 1:
            self.rightMotorSaturation = speed

    #Takes a list of all the balls in the arena, and determines which the robot can see.
    def detectBalls( self, balls ):
        self.sightedBalls = [] #Clear out the sighted balls
        for ball in balls:
            #Find the theta of the of the ball with respect to the polar coordante system centered on the robot.
            r, theta = toPolar( ball.y - self.y, ball.x - self.x )
            theta = self.heading - theta
            
            #Make sure theta is between -pi and pi            
            while theta > pi:
                theta += -2 * pi
            while theta < -1 * pi:
                theta += 2 * pi

            #If the camera is pointing close to the ball, we see it!
            if abs( theta ) < self.maxSightingAngle:
                self.sightedBalls.append( (r, theta) )
                ball.isSighted = True
            else:
                ball.isSighted = False

class Ball( Object ):
    def __init__( self, position, robot ):
        self.x, self.y = position
        self.robot = robot
        #Designates if the ball has been spotted by the camera this step so coloring can change.
        self.isSighted = False
    def step( self ):
        pass
    def draw( self, screen ):
        color = (255, 0, 0)
        if self.isSighted:
            color = (255, 255, 0 )
        pygame.draw.circle( screen, color, ( int( PIXELS_PER_INCH * self.x ), int( PIXELS_PER_INCH * self.y ) ), int( PIXELS_PER_INCH * 0.875 ) )
    
from blargh import Blargh

#Fake blargh to wrap the simulator in the Blargh.
class VisionBlargh(Blargh):
    def __init__(self, simulator):
        self.simulator = simulator

    def step(self, inp):
       return self.simulator.robot.detectBalls( simulator.balls )

if __name__ == "__main__":
    S = Simulator()
    S.robot.leftMotorSaturation = 1
    S.robot.rightMotorSaturation = 0.3
    while True:
        S.step()
        S.draw()
