import arduino
import camera
import cv

# Class to interact directly with the camera
class Camera():
    def __init__(self,cameraNumber):
        # Initialize the camera capture
        # 0 is the camera on the eeeeeeepc
        # 1 is the external camera
        self.capture = cv.CaptureFromCAM(cameraNumber)    
        self.mode = 1

    def updateImage(self):
        # Updates the image from the camera
        # Maybe should have some sort of delay/sleep
        # to indicate the time required to update?
        self.image = cv.QueryFrame(capture)
        if (self.mode == 1): #HSV mode
            cv.CvtColor(self.image,self.image,CV_RGB2HSV)

    def getImage(self):
        # Returns the current stored image
        # Remember to update image as well
        return self.image

    def setImage(self, image):
        # Used for unit testing
        self.image = image

    def setMode(self, mode):
        # 0 is RGB, 1 is HSV
        self.mode = mode

    
    
        
