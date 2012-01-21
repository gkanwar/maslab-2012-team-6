#Simululator Code.

import pygame
import math
import time

PIXELS_PER_INCH = 10

class Simulator:
    def __init__(self):
        # Initialize variables
        self.robot = Robot( 30, 30 )
        self.objects = [ self.robot ]

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

class Object():
    def step( self ):
        pass

    #No invisible objects
    def draw( self, screen ):
        raise NotImplementedError

class Robot( Object ):
    """ Class to keep track of the robot. """
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

    def setCoords(self, x, y):
        """ Set the x, y coords of the robot. """
        self.x = x
        self.y = y

S = Simulator()
S.robot.leftMotorSaturation = 1.0
S.robot.rightMotorSaturation = 0.3
while True:
    S.step()
    S.draw()
