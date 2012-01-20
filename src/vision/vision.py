import opencv
import cv
from opencv import highgui
from ctypes import cdll
lib = cdll.LoadLibrary('./libvision.so')

class Vision(object):
    def __init__(self):
        self.camera = highgui.cvCreateCameraCapture(0)
        highgui.cvNamedWindow("HelloWorld", cv.CV_WINDOW_AUTOSIZE)
        #self.obj = lib.createObj()

    def processBalls(self):
        img = highgui.cvQueryFrame(self.camera)
        highgui.cvShowImage("HelloWorld", img)
        highgui.cvWaitKey(10)

    #    lib.processBalls(self.obj)
    #def getNumBalls(self):
    #    return lib.ImageProcessing_getNumBalls(self.obj)
    #def getR(self, index):
    #    return lib.ImageProcessing_getR(self.obj, index);
    #def getTheta(self, index):
    #    return lib.ImageProcessing_getTheta(self.obj, index);

v = Vision()
while True:
    v.processBalls()
