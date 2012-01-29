from blargh import Blargh
import time

#This object will be passed on to the BehaviorBlargh. It describes the state of the world around the robot.
class World:
    def __init__(self, startTime):
        self.balls = []
        self.irData = None
        self.bumpData = None
        self.startTime = startTime
        self.time = 0
        self.wallInFront = False
        self.yellowPos = -1;
    def updateBalls(self, balls):
        self.balls = balls
    def updateYellowPos(self, position):
        self.yellowPos = position
    def updateBumpData(self, bumpData):
        self.bumpData = bumpData
    def updateIRData(self, irData):
        self.irData = irData
    def updateTime(self, time):
        self.time = time - self.startTime
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
        self.world = World(time.time())

    def step(self, inp):
        if (not inp == None):
            command, args = inp
            if (command == self.VISION):
                if args == None:
                    return None
                self.world.updateBalls(args[0])
                self.world.updateYellowPos(args[1])

            elif(command == self.INPUT):
                bumpData, irData = args
                if bumpData != None:
                    self.world.updateBumpData(bumpData)
                if irData != None:
                    self.world.updateIRData(irData)
        self.world.updateTime(time.time())
        return self.world
                

