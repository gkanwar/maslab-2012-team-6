from ctypes import *
# Load the C++ library
import os
visionlib = cdll.LoadLibrary(os.path.dirname(os.path.abspath(__file__)) + '/libvision.so')
# Set the return types
visionlib.init.restype = c_int
visionlib.processBalls.restype = c_int
visionlib.getR.restype = c_float
visionlib.getTheta.restype = c_float
visionlib.getTheta.restype = c_float

# Provide a python interface to the library, used by VisionBlargh
class Vision(object):
    # Create the ImageProcessing object in C++
    def __init__(self):
        visionlib.init()
        import time
        time.sleep(1)
    # Process a frame in C++
    def processBalls(self):
        visionlib.processBalls()
    # Get the number of balls found
    def getNumBalls(self):
        return visionlib.getNumBalls()
    # Get the r for a specific ball found
    def getR(self, index):
        return visionlib.getR(index)
    # Get the theta for a specific ball found
    def getTheta(self, index):
        return visionlib.getTheta(index)
    # Get the center of all yellow that we see
    def getYellowCenterT(self):
        return visionlib.getYellowCenterT()


# Example code

if __name__ == "__main__":
    v = Vision()
    while True:
        v.processBalls()
        for i in range(v.getNumBalls()):
            print (i, v.getR(i), v.getTheta(i))
