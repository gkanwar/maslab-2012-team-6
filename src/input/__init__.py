from blargh import Blargh
from exceptions import Exception

# Gets input from the arduinoInterfaceInputWrapper and possibly processes it
# to some degree
class InputBlargh(Blargh):
    def __init__(self, arduinoInterfaceInputWrapper):
        self.aiiw = arduinoInterfaceInputWrapper
        self.frontBumpNumber = 0

    # Get input from aiiw and possible process it
    def step(self, inp):
        print "InputBlargh: stepped"
        out = self.aiiw.getBumpHit(self.frontBumpNumber)
        print "InputBlargh: got output", out
        return out
