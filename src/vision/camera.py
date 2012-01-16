import sys
sys.path.append("..")
import arduino
import camera
import cv
import array

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
        self.image = cv.QueryFrame(self.capture)
        cv.CvtColor(self.image,self.image,cv.CV_RGB2HSV)
        imageDat = array.array('B',self.image.tostring())
        imageData = imageDat.tolist()
        print ( len (imageData))
        width = self.image.width
        print width
        height = self.image.height
        print height
        nChannels = self.image.nChannels
        print nChannels
        step = width * nChannels
        for i in range(height):
            for j in range(width):
                #normalize lumonosity
                index = int(i*step) + int(j*nChannels)
                print(index)
                print(len(imageData))
                imageData[index +int(0)] = chr ( imageData[index + 0])
                imageData[index + int(1)] = chr ( imageData[index + 1])
                imageData[index + 2] = chr ( 40)
#        self.image = str(imageData).replace("[","").replace("
        
    def getImage(self):
        # Returns the current stored image
        # Remember to update image as well
        return self.image

    def setImage(self, image):
        # Used for unit testing
        self.image = image


    
    
        
