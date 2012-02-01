from blargh import Blargh
from math import pi
import time

STATE_CHANGE_FLAG = 0
DEAD_STATE_FLAG = 1

def capVal(val, maximum, minimum):
    if (val > maximum):
        val = maximum
    elif (val < minimum):
        val = minimum
    return val

class ControlBlargh(Blargh):
    
    def __init__(self, arduinoInterface):
        self.arduinoInterface = arduinoInterface
        self.angleThreshold = pi / 16
        self.driveThreshold = .3
        self.rollerSpeed = 50
        # Old values
        #self.anglePID = PID((30,0,0))
        #self.drivePID = PID((.04,0,0))
        self.anglePID = PID((.5,0,0), .75)
        self.drivePID = PID((.5,0,0), .75)
        self.goal = None
        self.maxMotorSpeed = 1

    def step(self, goal):

        if not goal == None:
            self.goal = goal
            if self.goal == STATE_CHANGE_FLAG:
                print "Changing States!"
                self.arduinoInterface.setMotorSpeed(2, self.rollerSpeed)
                self.anglePID.reset()
            elif self.goal == DEAD_STATE_FLAG:
                self.arduinoInterface.setMotorSpeed(2, 0)
                goal = (0,0)
            else:
                self.arduinoInterface.setMotorSpeed(2, self.rollerSpeed)
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

                if (theta < self.angleThreshold):
                    aval = self.anglePID.update(theta)
                    dval = self.drivePID.update(r)
                    motor0Speed = aval+dval
                    motor1Speed = aval-dval
                    motor0Speed = capVal(dval+aval, self.maxMotorSpeed, -self.maxMotorSpeed)
                    motor1Speed = capVal(dval-aval, self.maxMotorSpeed, -self.maxMotorSpeed)
                else:
                    aval = self.anglePID.update(theta)
                    motor0Speed = capVal(aval, self.maxMotorSpeed, -self.maxMotorSpeed)
                    motor1Speed = capVal(-aval, self.maxMotorSpeed, -self.maxMotorSpeed)

                self.arduinoInterface.setMotorSpeed(0, motor0Speed)
                self.arduinoInterface.setMotorSpeed(1, motor1Speed)

class PID:

    def __init__(self, pidtuple, cap):
        self.P = pidtuple[0]
        self.I = pidtuple[1]
        self.D = pidtuple[2]
        self.cap = cap
        self.lastVal = 0
        self.sumErr = 0
        self.startTime = time.time()
        self.prevTime = time.time()
    
    def update(self, setPoint):
        currTime = time.time()
        while (currTime == self.prevTime):
            currTime = time.time()
        self.linErr = setPoint

        """
        self.divErr = (self.lastVal - setPoint) / (currTime - self.prevTime)
        self.lastval = setPoint
        self.sumErr += setPoint * (currTime - self.prevTime)
        """

        #print "Hi Will!", self.linErr, self.divErr
        pval = self.P*self.linErr # + self.D*self.divErr
        if(pval>=self.cap):  
            pval = self.cap
        if(pval<=-self.cap):
            pval = -self.cap
        return pval
    def reset( self ):
        self.startTime = time.time()
        self.prevTime = time.time()
        self.sumErr = 0
