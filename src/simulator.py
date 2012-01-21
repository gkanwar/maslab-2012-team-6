#Simululator Code.

import pygame
import math
import time
import random

PIXELS_PER_INCH = 10

class Simulator:
    def __init__(self):
        # Initialize variables
        #The robot is on it's own for convinence in later access.
        self.robot = Robot( ( 30, 30 ) )
        self.objects = []
        for i in range( 12 ):
            self.objects.append( Ball( ( random.randint( 0, 60 ), random.randint( 0, 60 ) ) ) )
        self.objects.append( self.robot )

        self.xSize = 60
        self.ySize = 60

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
    """Simulates the physical robot. The robot should be implemented in such a way that it can interface with code in the same way as the Arduino wrapper(s)"""
    def __init__( self, position ):
        self.x, self.y = position

        self.radius = 7
        
        self.lastTime = time.time()

        #robot heading in radians
        self.heading = 0

        #motor info
        self.leftMotorSaturation = 0
        self.rightMotorSaturation = 0

        self.maxMotorSpeed = 20

    #Update the Robot's position
    def step( self ):
        currentTime = time.time()
        delTime = currentTime - self.lastTime

        #I'm assuming this function gets called pretty often, so I can decouple.
        avgSpeed = self.maxMotorSpeed * ( self.leftMotorSaturation + self.rightMotorSaturation ) / 2
        self.x += delTime * avgSpeed * math.sin( self.heading )
        self.y += delTime * avgSpeed * math.cos( self.heading )

        #That's right. Radians, bitches.
        self.heading += self.maxMotorSpeed * delTime * ( self.leftMotorSaturation - self.rightMotorSaturation ) / ( 2 * self.radius )
        
        self.lastTime = currentTime

    def draw( self, screen ):
        pygame.draw.circle( screen, (0, 0, 255), ( int( PIXELS_PER_INCH * self.x ), int( PIXELS_PER_INCH * self.y ) ), int( PIXELS_PER_INCH * self.radius ) )
        pygame.draw.line( screen, (0, 255, 0), ( int( PIXELS_PER_INCH * self.x ), int( PIXELS_PER_INCH * self.y ) ), ( int( PIXELS_PER_INCH * ( self.x + ( self.radius * math.sin( self.heading ) ) ) ), int( PIXELS_PER_INCH * ( self.y + ( self.radius * math.cos( self.heading ) ) ) ) ) )

    def setMotorSpeed( self, motorNum, speed ):
        if motorNum == 0:
            self.leftMotorSaturation = speed
        elif motorNum == 1:
            self.rightMotorSaturation = speed

class Ball( Object ):
    def step( self ):
        pass
    def draw( self, screen ):
        pygame.draw.circle( screen, (255, 0, 0), ( int( PIXELS_PER_INCH * self.x ), int( PIXELS_PER_INCH * self.y ) ), int( PIXELS_PER_INCH * 0.875 ) )
    

S = Simulator()
S.robot.leftMotorSaturation = 1.0
S.robot.rightMotorSaturation = 0.3
while True:
    S.step()
    S.draw()
