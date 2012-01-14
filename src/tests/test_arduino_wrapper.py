import sys
sys.path.append("../../lib")
sys.path.append("..")
from arduino import *

aw = ArduinoWrapper()
aw.start()
print "Bump sensor:", aw.bumpSensors[0].getValue()
