from blargh import Blargh
from exceptions import Exception

# Gets input from the arduinoInterfaceInputWrapper and possibly processes it
# to some degree
class InputBlargh(Blargh):
    bumpSensors = []
    def __init__(self, arduinoInterfaceWrapper):
        self.ardInWrapper = arduinoInterfaceWrapper
        

    # Get input from aiw and possible process it
    def step(self, inp):
        # print "InputBlargh: stepped"
        bumpData = BumpSensorData()
        irData = IRData()
        bumpData.left = self.ardInWrapper.getBumpHit(0)
        bumpData.right= self.ardInWrapper.getBumpHit(1)
        return (1,(bumpData, irData))

class BumpSensorData():
    left = False
    right= False
    back = False
    def __init__(self):
        pass

class IRData():
    # Meh probably should be like -1 by default but this works too
    front = 1000
    def __init__(self):
        pass


