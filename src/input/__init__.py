from blargh import Blargh
from exceptions import Exception

class InputBlargh(Blargh):
    def __init__(self, arduinoInterfaceInputWrapper):
        self.aiiw = arduinoInterfaceInputWrapper
        self.frontBumpNumber = 0

    def step(self, inp):
        print "InputBlargh: stepped"
        out = self.aiiw.getBumpHit(self.frontBumpNumber)
        print "InputBlargh: got output", out
        return out
