from blargh import Blargh
from math import pi
import time

STATE_CHANGE_FLAG = 0

class ControlBlargh(Blargh):
    
    def __init__(self, arduinoInterface):
        self.arduinoInterface = arduinoInterface
        self.angleThreshold = pi / 16
        self.driveThreshold = .3
        # Old values
        #self.anglePID = PID((1,0,0))
        #self.drivePID = PID((.04,0,0))
        self.anglePID = PID((2,0,0))
        self.drivePID = PID((.02,0,0))
        self.goal = None
        self.maxMotorSpeed = 0.6
    STATE_CHANGE_FLAG = 0
    def step(self, goal):
        if not goal == None:
            self.goal = goal
        if not self.goal == None:
            if self.goal == STATE_CHANGE_FLAG:
                # print "Changing States!"
                self.anglePID.reset()
            else:
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
                if(aval + dval >= self.maxMotorSpeed):
                    self.arduinoInterface.setMotorSpeed(0, self.maxMotorSpeed)
                elif(aval + dval <=-self.maxMotorSpeed):
                    self.arduinoInterface.setMotorSpeed(0, -self.maxMotorSpeed)
                else:
                    self.arduinoInterface.setMotorSpeed(0, aval + dval)
                    
                if(dval - aval >= self.maxMotorSpeed):
                    self.arduinoInterface.setMotorSpeed(1, self.maxMotorSpeed)
                elif(dval - aval <=-self.maxMotorSpeed):
                    self.arduinoInterface.setMotorSpeed(1, -self.maxMotorSpeed)
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
    def reset( self ):
        self.startTime = time.time()
        self.sumErr = 0
