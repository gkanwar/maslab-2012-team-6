from blargh import Blargh
import time
# comment here


class ControlBlargh(Blargh):
    
    def __init__(self, arduinoInterface):
        self.arduinoInterface = arduinoInterface
        self.angleThreshold = .2
        self.driveThreshold = .3
        self.anglePID = PID(self, (.2,0,0))
        self.drivePID = PID(self, (.3,0,0))
    
    def step(self, goal):
        if(goal[0]>angleThreshold)
            pval = anglePID(goal[0])
            self.arduinoInterface.setMotorSpeed(0, pval)
            self.arduinoInterface.setMotorSpeed(1, -pval)
        if(goal[1]>driveThreshold)
            pval = drivePID(goal[1])
            self.arduinoInterface.setMotorSpeed(0, pval)
            self.arduinoInterface.setMotorSpeed(1, pval)


class PID:

    def __init__(self, pidtuple):
        self.P = pidtuple[0]
        self.I = pidtuple[1]
        self.D = pidtuple[2]
        self.lastVal = 0
        self.sumErr = 0
        self.startTime = time.time()
        self.prevTime = time.time()
    
    def update(self, stpt):
        currTime = time.time()
        self.linErr = stpt
        self.divErr = (lastval - stpt) / (currTime - self.prevTime)
        self.lastval = stpt
        self.sumErr += stpt * (currTime - self.prevTime)
        self.intErr = sumErr / (currTime - self.startTime)
        self.prevTime = currTime 
        pval = P*linErr + I*intErr + D*divErr
        if(pval>=1):  
            pval = 1
        if(pval<=-1):
            pval = -1
        return pval
