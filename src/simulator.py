#Simululator Code.

import pygame
import math
import time

PIXELS_PER_INCH = 10

class Simulator:
    def __init__(self):
        # Initialize variables
        self.map = Map()
        self.robot = Robot( 30, 30 )

        self.xSize = 60
        self.ySize = 60

        # Initialize pygame for visualization
        pygame.init()
        self.screen = pygame.display.set_mode( ( PIXELS_PER_INCH * self.xSize, PIXELS_PER_INCH * self.ySize ) )

    def draw(self):
        """
        Use the pygame library to draw the world and the robot.
        """
        # Clear the screen
        self.screen.fill( (0, 0, 0) )

        # Draw the robot
        pygame.draw.circle( self.screen, (0, 0, 255), ( int( PIXELS_PER_INCH * self.robot.x ), int( PIXELS_PER_INCH * self.robot.y ) ), int( PIXELS_PER_INCH * self.robot.radius ) )
        pygame.draw.line( self.screen, (0, 255, 0), ( int( PIXELS_PER_INCH * self.robot.x ), int( PIXELS_PER_INCH * self.robot.y ) ), ( int( PIXELS_PER_INCH * ( self.robot.x + ( self.robot.radius * math.sin( self.robot.heading ) ) ) ), int( PIXELS_PER_INCH * ( self.robot.y + ( self.robot.radius * math.cos( self.robot.heading ) ) ) ) ) )
        #Flip the buffers (display everything)
        pygame.display.flip()

class Robot():
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

    def setMotorSpeed( self, motorNum, speed ):
        if motorNum == 0:
            self.leftMotorSaturation = speed
        elif motorNum == 1:
            self.rightMotorSaturation = speed

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

    def setCoords(self, x, y):
        """ Set the x, y coords of the robot. """
        self.x = x
        self.y = y

class Map():
    def __init__(self):
        self.maxX = 0
        self.maxY = 0
        self.minX = 0
        self.minY = 0
        self.wallGrid = {}
        self.ballGrid = {}


    # Overload the [] operator
    def __getitem__(self, key):
        if (key in self.wallGrid.keys()):
            val1 = self.grid[key]
        else:
            val1 = None
        if (key in self.ballGrid.keys()):
            val2 = self.grid[key]
        else:
            val2 = None
        return (val1, val2)
    def __setitem__(self, key, value):
        val1, val2 = value
        wallGrid[key] = val1
        ballGrid[key] = val2

    def setRobotLocation(self, x, y):
        """ Set the robot location to an arbitrary x, y coord. """
        self.robot.setLocation(x, y)
        self.expandMapForRobot()

    def translateRobot(self, dx, dy):
        """ Set the robot location to be dx, dy greater than before. """
        self.robot.translate(dx, dy)
        self.expandMapForRobot()

    def expandMapForRobot(self):
        """ Expand the map to make sure the robot coords are in it """
        self.expandMapForCoord(self.robot.x, self.robot.y)

    def expandMapForCoord(self, x, y):
        """ Expand the map to make sure the coord is inside it. """
        if (x > self.maxX):
            self.maxX = x
        elif (x < self.minX):
            self.minX = x
        if (y > self.maxY):
            self.maxY = y
        elif (y < self.minY):
            self.minY = y

    def getAngleBetweenCoords(x1, y1, x2, y2):
        return atan2(x2 - x1, y2 - y1)

S = Simulator()
S.robot.leftMotorSaturation = 1.0
S.robot.rightMotorSaturation = 0.3
while True:
    S.robot.step()
    S.draw()
