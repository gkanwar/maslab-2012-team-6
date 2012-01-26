from blargh import Blargh
import time

#This object will be passed on to the BehaviorBlargh. It describes the state of the world around the robot.
class World:
    def __init__( self, balls, bumpData, irData, time, wallInFront ):
        self.balls = balls
        self.irData = irData
        self.bumpData = bumpData
        self.time = time
        self.hitWall = False
    def isWallInFront( self ):
        return self.hitWall
        

#This Blargh takes input from the sensors and vision and aggregates it into a model of the world.
#For now, this is pretty sparse. Just pass on data.
class WorldBlargh( Blargh ):
    def __init__( self ):
        self.startTime = time.time()
    def step( self, inp ):
        if ( not inp == None ):
            command, args = inp
        else:
            print "No Input!"
            #world = World( None, None, None, time.time() - self.startTime, False)
            #return world
            return None
        if (command == 0):
            if args == None:
                # world = World( None, None, None, time.time() - self.startTime, False)
                # return world
                return None
            self.balls = args
            world = World( args, None, None, time.time() - self.startTime, False)
            return world
        elif(command == 1):
            if args[0] == None:
                # world = World( None, None, None, time.time() - self.startTime, False)
                # return world
                return None
            elif args[1] == None:
                # world = World( None, None, None, time.time() - self.startTime, False)
                # return world
                return None
            else:
                world = World(None,args[0],args[1],
                                   time.time() - self.startTime,False)
                return world
                

