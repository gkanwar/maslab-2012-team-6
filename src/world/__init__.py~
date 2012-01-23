from blargh import Blargh
import time

#This object will be passed on to the BehaviorBlargh. It describes the state of the world around the robot.
class World:
    def __init__( self, balls, time, wallInFront ):
        self.balls = balls
        self.time = time
        self.hitWall = False
    def isWallInFront( self ):
        return self.hitWall
        

#This Blargh takes input from the sensors and vision and aggregates it into a model of the world.
#For now, this is pretty sparse. Just pass on data.
class WorldBlargh( Blargh ):
    def __init__( self ):
        self.startTime = time.time()
    def step( self, balls ):
        if balls == None:
            return None
        world = World( balls, time.time() - self.startTime, False)
        return world
