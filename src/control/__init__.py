from blargh import Blargh
from math import pi
import time

class ControlBlargh(Blargh):
    
    def __init__(self, arduinoInterface):
        self.arduinoInterface = arduinoInterface
        self.angleThreshold = pi / 12
        self.driveThreshold = .3
        self.anglePID = PID((20,20,0))
        self.drivePID = PID((.15,0,0))
        self.goal = None
    
    def step(self, goal):
        if not goal == None:
            self.goal = goal
        if not self.goal == None:
            if self.goal == (1,0):
                self.anglePID = PID((5,0,0))
            else:
                self.anglePID = PID((20,20,0))
            r, theta = self.goal
            # Make sure theta is between -pi and pi to avoid spinning in circles.
            while theta > pi:
                theta += -2 * pi
            while theta < -1 * pi:
                theta += 2 * pi
            '''if(abs(theta)>self.angleThreshold):
                pval = self.anglePID.update(theta)
                self.arduinoInterface.setMotorSpeed(0, pval)
                self.arduinoInterface.setMotorSpeed(1, -pval)
            elif(abs(r)>self.driveThreshold):
                pval = self.drivePID.update(r)
                self.arduinoInterface.setMotorSpeed(0, pval)
                self.arduinoInterface.setMotorSpeed(1, pval)
            else:
                self.arduinoInterface.setMotorSpeed(0, 0)
                self.arduinoInterface.setMotorSpeed(1, 0)'''
            #HACK - ?
            aval = self.anglePID.update(theta)
            dval = self.drivePID.update(r)
            if(aval + dval >=1):
                self.arduinoInterface.setMotorSpeed(0, 1)
            elif(aval + dval <=-1):
                self.arduinoInterface.setMotorSpeed(0, -1)
            else:
                self.arduinoInterface.setMotorSpeed(0, aval + dval)
                
            if(dval - aval >=1):
                self.arduinoInterface.setMotorSpeed(1, 1)
            elif(dval - aval <=-1):
                self.arduinoInterface.setMotorSpeed(1, -1)
            else:
                self.arduinoInterface.setMotorSpeed(1, dval - aval)


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
        self.divErr = (self.lastVal - stpt) / (currTime - self.prevTime)
        self.lastval = stpt
        self.sumErr += stpt * (currTime - self.prevTime)
        self.intErr = self.sumErr / (currTime - self.startTime)
        self.prevTime = currTime 
        pval = self.P*self.linErr + self.I*self.intErr + self.D*self.divErr
        '''if(pval>=1):  
            pval = 1
        if(pval<=-1):
            pval = -1'''
        return pval
