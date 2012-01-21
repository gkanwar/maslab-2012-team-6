from blargh import Blargh
'''import pygame

class WorldBlargh(Blargh):
    """
    Class to take in input from various sources and generate a probability map
    of where walls and balls are likely to be relative to the robot.
    """

    # Constants
    BOX_WIDTH = 20
    ROBOT_WIDTH = 5

    def __init__(self):
        # Initialize variables
        self.map = Map()

        # Initialize pygame for visualization
        pygame.init()
        self.screen = pygame.display.set_mode(((self.maxX - self.minX)*self.BOX_WIDTH, (self.maxY - self.minY)*self.BOX_WIDTH))

    # This is the brains of the robot -- let's make it good!
    def step(self, inp):
        type, inp = inp
        # If we're getting vision input
        if (type == "CAMERA"):
            self.map.updateBallProb(inp)
        # If we're getting other sort of input (none of which we're dealing
        # with now)
        else:
            pass

        # Return the Map object
        return ("MAP", self.map)

    ################## NOT USING THIS FOR MOCK 1 ####################
    def showMap(self):
        """
        Use the pygame library to draw a visual representation of the robot's
        belief about what the world looks like.
        """
        # Clear the screen
        self.screen.fill((0, 0, 0))
        # Draw all the grid boxes
        for x in range(self.minX, self.maxX+1):
            for y in range(self.minY, self.maxY+1):
                # Create a border and a smaller inner box
                box_border = pygame.Surface((self.BOX_WIDTH, self.BOX_WIDTH))
                box_border = box_border.convert()
                box_border.fill((0, 0, 0))
                box = pygame.Surface((self.BOX_WIDTH-2, self.BOX_WIDTH-2))
                box = box.convert()
                # Fill in the box color based on the probability of that
                # grid location being a wall
                val = self.map[(x, y)]
                if (val != None):
                    box.fill((val, val, val))
                else:
                    box.fill((0, 0, 255))
                # Blit in the box and border
                self.screen.blit(box_border, (x*self.BOX_WIDTH, y*self.BOX_WIDTH))
                self.screen.blit(box, (x*self.BOX_WIDTH + 1, y*self.BOX_WIDTH + 1))

        # Draw the robot
        robotBox = pygame.Surface((self.ROBOT_WIDTH, self.ROBOT_WIDTH))
        robotBox.fill((255, 255, 0))
        self.screen.blit(robotBox, (self.map.robot.x*self.BOX_WIDTH + (self.BOX_WIDTH - self.ROBOT_WIDTH)/2, self.map.robot.y*self.BOX_WIDTH + (self.BOX_WIDTH - self.ROBOT_WIDTH)/2))

        # Flip the buffers (display everything)
        pygame.display.flip()



class Robot():
    """ Class to keep track of the location of the robot. """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translate(self, dx, dy):
        """ Translate the robot and return the new coords. """
        self.x += dx
        self.y += dy
        return (self.x, self.y)

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
        self.robot = Robot(0, 0)

    def updateBallProb(self, ballLocs):
        # Temporary code
        self.ballGrid = {}
        for x, y in ballLocs:
            self.ballGrid[(x, y)] = 1.0
            self.expandMapForCoord(x, y)

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
'''

#This object will be passed on to the BehaviorBlargh. It describes the state of the world around the robot.
class World:
	def __init__( self, balls, wallInFront ):
		self.balls = balls
		self.wallInFront = wallInFront
	def isWallInFront( self ):
		return self.wallInFront
		

#This Blargh takes input from the sensors and vision and aggregates it into a model of the world.
#For now, this is pretty sparse. Just pass on data.
class WorldBlargh( Blargh ):
	def step( inp ):
		world = World( [], False)
		return world
	
# Testing code
if __name__ == "__main__":
    '''mb = WorldBlargh()
    import time
    for i in range(15):
        mb.translateRobot(1, 0)
        mb.showMap()
        time.sleep(1)'''
