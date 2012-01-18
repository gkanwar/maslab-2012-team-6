#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <opencv/cv.h>
#include <opencv/highgui.h>
#include <vector>
using namespace std;

#define redThreshold 90
#define blueThreshold 30
#define smoothFrames 2
#define imageWidth 640
#define imageHeight 480
#define viewPort 50
vector<float> returnValues;

class ImageProcessing
{
    public:
        // Create some class variables
        CvCapture* capture;
        IplImage* frame;
        
        ImageProcessing()
        {
            // Set up the capture
            capture = cvCaptureFromCAM(1);

            // Make some windows
            cvNamedWindow("Original", CV_WINDOW_AUTOSIZE);
        }

        void processBalls()
        {
            frame = cvQueryFrame(capture);
            cvShowImage("Original", frame);
            cvWaitKey(10);
        }
        int getR(int index)
        {
            return returnValues[index * 2 + 1];
        }
        int getTheta(int index)
        {
            return returnValues[index*2 + 1 + 1];
        }
};

extern "C"
{
    ImageProcessing* createObj() { return new ImageProcessing(); }
    void processBalls(ImageProcessing* ip) { ip->processBalls(); }
    //int ImageProcessing_getR(ImageProcessing* ip,int index){ ip->getR(index); }
    //int ImageProcessing_getTheta(ImageProcessing * ip,int index){ ip->getTheta(index); }
    //int ImageProcessing_getNumBalls( ImageProcessing* ip){ip->getNumBalls();}
}

