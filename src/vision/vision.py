from ctypes import cdll
lib = cdll.LoadLibrary('./libvision.so')

class Vision(object):
    def __init__(self):
        self.obj = lib.ImageProcessing_new()

    def processBalls(self):
        lib.ImageProcessing_processBalls(self.obj)
    #def getNumBalls(self):
    #    return lib.ImageProcessing_getNumBalls(self.obj)
    #def getR(self, index):
    #    return lib.ImageProcessing_getR(self.obj, index);
    #def getTheta(self, index):
    #    return lib.ImageProcessing_getTheta(self.obj, index);

v = Vision()
while True:
    v.processBalls()
