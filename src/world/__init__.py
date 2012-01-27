from blargh import Blargh
import time

#This object will be passed on to the BehaviorBlargh. It describes the state of the world around the robot.
class World:
    def __init__(self):
        self.balls = []
        self.irData = None
        self.bumpData = None
        self.time = 0
        self.wallInFront = False
    def updateBalls(self, balls):
        self.balls = balls
    def updateBumpData(self, bumpData):
        self.bumpData = bumpData
    def updateIRData(self, irData):
        self.irData = irData
    def updateTime(self, time):
        self.time = time
    def updateWallInFront(self, wallInFront):
        self.wallInFront = wallInFront
    def isWallInFront(self):
        return self.wallInFront
        

#This Blargh takes input from the sensors and vision and aggregates it into a model of the world.
#For now, this is pretty sparse. Just pass on data.
class WorldBlargh(Blargh):
    VISION = 0
    INPUT = 1
    def __init__(self):
        self.world = World()
        self.startTime = time.time()
    def step(self, inp):
        if (not inp == None):
            command, args = inp
            if (command == self.VISION):
                if args == None:
                    return None
                self.world.updateBalls(args)
            elif(command == self.INPUT):
                if args[0] != None:
                    self.world.updateBumpData(args[0])
                if args[1] != None:
                    self.world.updateIRData(args[1])
        self.world.updateTime(time.time() - self.startTime)
        return self.world
                

