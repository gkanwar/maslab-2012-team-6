class World:
    def __init__( self, balls, bumpData, irData, time, wallInFront ):
        self.balls = balls
        #print time
        self.time = time
        self.wallInFront = wallInFront
    def isWallInFront( self ):
        return self.wallInFront

world = World( [], None, None, 0, False )

class State(object):
    def step(self):
        if world.time > 179:
            return DeadState(), STATE_CHANGE_FLAG
        if world.isWallInFront():
            return EscapeState(), STATE_CHANGE_FLAG
        else:
            return None,None
