from opencv.cv import *
from opencv.highgui import *

class Vision(object):

    # Constants
    IMG_WIDTH = 640
    IMG_HEIGHT = 480

    def __init__(self):
        # Create a camera capture
        self.camera = cvCreateCameraCapture(0)
        # Create some named windows
        cvNamedWindow("Original", CV_WINDOW_AUTOSIZE)
	cvNamedWindow("Output", CV_WINDOW_AUTOSIZE)
	cvNamedWindow("Intermediate", CV_WINDOW_AUTOSIZE)
	cvNamedWindow("Int2", CV_WINDOW_AUTOSIZE)
	cvNamedWindow("Ellipse", CV_WINDOW_AUTOSIZE)
        # Create our memStorages
        self.contourStorage = cvCreateMemStorage(0)
	self.houghStorage = cvCreateMemStorage(0)
	self.pointStorage = cvCreateMemStorage(0)
        # Create our images
	self.hsvImage = cvCreateImage((self.IMG_WIDTH, self.IMG_HEIGHT), IPL_DEPTH_8U, 3)
        self.normalized = cvCreateImage((self.IMG_WIDTH, self.IMG_HEIGHT), IPL_DEPTH_8U, 3)
    def processBalls(self):
        # Query the frame
        frame = cvQueryFrame(self.camera)
        # Show it (for reference)
        cvShowImage("Original", frame)

        # Normalize luminosity
        # Convert from BGR to HSV
        cvCvtColor(frame, self.hsvImage, CV_BGR2HSV)
        # Split the hsvImage
        hue = cvCreateMat(frame.height, frame.width, CV_8UC1)
        sat = cvCreateMat(frame.height, frame.width, CV_8UC1)
        val = cvCreateMat(frame.height, frame.width, CV_8UC1)
        cvSplit(self.hsvImage, hue, sat, val, None)
        # Create a one channel matrix
        valMat = cvCreateMat(frame.height, frame.width, CV_8UC1)
        cvSet(valMat, 200)
        cvMerge(hue, sat, valMat, None, self.hsvImage)
        # Convert the back to BGR
        cvCvtColor(self.hsvImage, self.normalized, CV_HSV2BGR)
        # Show it
        cvShowImage("Int2", self.normalized)

        # Filter the image for red balls
        """
        ballArr = []
        ballImage = cvCreateImageHeader(self.normalized.width * self.normalized.height, IPL_DEPTH_8U, 3)
        for i in range(self.normalized.height):
            for j in range(self.normalized.width):
                ballImageIndex = i * ballImage.widthStep + j * ballImage.nChannels
                normIndex = i * self.normalized.widthStep + j * self.normalized
                if (max(self.normalized.data[normIndex], self.normalized.data[normIndex+1])
                       < self.normalized.data[normIndex+2]):
                    ballArr.append(0)
                    ballArr.append(0)
                    ballArr.append(255)
                else:
                    ballArr.append(0)
                    ballArr.append(0)
                    ballArr.append(0)
        cvSetData(ballImage, ballArr)
        # Show it
        cvShowImage("Intermediate", ballImage)
        """

        # Wait to make sure the showing of the image doesn't break
        cvWaitKey(10)

v = Vision()
while True:
    v.processBalls()
