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
        print "InputBlargh: stepped"
        bumpData = BumpSensorData()
        irData = IRData()
        bumpData.left = self.ardInWrapper.getBumpHit(0)
        bumpData.right= self.ardInWrapper.getBumpHit(1)
        print "BumpData:", bumpData.left
        print "BumpData:", bumpData.right
        
        print "InputBlargh: got output"
        return (1,(bumpData, irData))

class BumpSensorData():
    left = False
    right = False
    back = False
    def __init__(self):
        pass

class IRData():
    front = 1000
    def __init__(self):
        pass
