from ctypes import *
# Load the C++ library
visionlib = cdll.LoadLibrary('./libvision.so')
# Set the return types
visionlib.createObj.restype = c_int
visionlib.processBalls.restype = c_int
visionlib.getR.restype = c_float
visionlib.getTheta.restype = c_float

# Provide a python interface to the library, used by VisionBlargh
class Vision(object):
    # Create the ImageProcessing object in C++
    def __init__(self):
        self.obj = visionlib.createObj()
    # Process a frame in C++
    def processBalls(self):
        visionlib.processBalls(self.obj)
    # Get the number of balls found
    def getNumBalls(self):
        return visionlib.getNumBalls(self.obj)
    # Get the r for a specific ball found
    def getR(self, index):
        return visionlib.getR(self.obj, index)
    # Get the theta for a specific ball found
    def getTheta(self, index):
        return visionlib.getTheta(self.obj, index)

# Example code
if __name__ == "__main__":
    v = Vision()
    while True:
        v.processBalls()
        for i in range(v.getNumBalls()):
            print (i, v.getR(i), v.getTheta(i))
