#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <opencv/cv.h>
#include <opencv/highgui.h>
#include <deque>
using namespace std;

#define NUM_FRAMES_TO_AVERAGE 2
#define RED_DISPARITY 60
#define RED_THRESHOLD 50

class ImageProcessing
{
    public:
        // Create some class variables
        CvCapture* capture;
        IplImage* frame;

        int numFrameCountdown;

        deque<IplImage*> pastFrames;

        ImageProcessing()
        {
            // Set up the capture
            capture = cvCaptureFromCAM(1);

            // Make some windows
            cvNamedWindow("Original", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Output", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Intermediate", CV_WINDOW_AUTOSIZE);
        }

        void processBalls()
        {
            // Get the frame
            frame = cvQueryFrame(capture);
            // Display it
            cvShowImage("Original", frame);

            // Remove noise by blurring - REDACTED!
            /*
            IplImage* temp = cvCreateImage(cvSize(320, 240), IPL_DEPTH_8U, 3);
            IplImage* cleanedUp = cvCreateImage(cvSize(640, 480), IPL_DEPTH_8U, 3);
            cvPyrDown(frame, temp, 7);
            cvPyrUp(temp, cleanedUp, 7);
            cvReleaseImage(&temp);
            // Display it
            cvShowImage("Output", cleanedUp);
            */

            // Remove noise by averaging frames - REDACTED!
            /*
            pastFrames.push_back(frame);
            if (pastFrames.size() > NUM_FRAMES_TO_AVERAGE)
            {
                pastFrames.pop_front();
            }
            IplImage* averaged = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            // Clear the image
            for (int i = 0; i < averaged->height; i++)
            {
                for (int j = 0; j < averaged->width; j++)
                {
                    int index = i * averaged->widthStep + j * averaged->nChannels;
                    averaged->imageData[index] = 0;
                    averaged->imageData[index+1] = 0;
                    averaged->imageData[index+2] = 0;
                }
            }
            // Average the frames
            for (int i = 0; i < frame->height; i++)
            {
                for (int j = 0; j < frame->width; j++)
                {
                    int averagedIndex = i * averaged->widthStep + j * averaged->nChannels;
                    if (pastFrames.size() > 0)
                    {
                        int pastFramesIndex = i * pastFrames[0]->widthStep + j * pastFrames[0]->nChannels;
                        float b = 0, g = 0, r = 0;
                        for (int k = 0; k < pastFrames.size(); k++)
                        {
                            b += pastFrames[k]->imageData[pastFramesIndex];
                            g += pastFrames[k]->imageData[pastFramesIndex+1];
                            r += pastFrames[k]->imageData[pastFramesIndex+2];
                        }
                        averaged->imageData[averagedIndex] = b/pastFrames.size();
                        averaged->imageData[averagedIndex+1] = g/pastFrames.size();
                        averaged->imageData[averagedIndex+2] = r/pastFrames.size();
                    }
                }
            }
            // Display it
            cvShowImage("Output", averaged);
            */

            // Normalize luminosity somewhat - REDACTED!
            /*
            IplImage* hsvImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            cvCvtColor(frame, hsvImage, CV_BGR2HSV);

            for (int i = 0; i < hsvImage->height; i++)
            {
                for (int j = 0; j < hsvImage->width; j++)
                {
                    int index = i * hsvImage->widthStep + j * hsvImage->nChannels;
                    hsvImage->imageData[index+2] = 50;
                }
            }

            IplImage* normalized = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            cvCvtColor(hsvImage, normalized, CV_HSV2BGR);

            cvShowImage("Output", normalized);
            */

            // Filter the image for red balls
            IplImage* ballImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            for (int i = 0; i < frame->height; i++)
            {
                for (int j = 0; j < frame->width; j++)
                {
                    int ballImageIndex = i * ballImage->widthStep + j * ballImage->nChannels;
                    int frameIndex = i * frame->widthStep + j * frame->nChannels;
                    uchar* imageData = (uchar*) frame->imageData;
                    if(imageData[frameIndex+2] >= imageData[frameIndex] + RED_DISPARITY
                          && imageData[frameIndex+2] >= imageData[frameIndex+1] + RED_DISPARITY
                          && imageData[frameIndex+2] >= RED_THRESHOLD)
                    {
                        ballImage->imageData[ballImageIndex] = 255;
                    }
                    else
                    {
                        ballImage->imageData[ballImageIndex] = 0;
                    }
                }
            }

            cvShowImage("Intermediate", ballImage);

            // Get contours in the image
            CvMemStorage* storage = cvCreateMemStorage(0);
            CvSeq* contours = NULL;
            cvFindContours(ballImage, storage, &contours);
            IplImage* contourImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            cvDrawContours(contourImage, contours, cvScalarAll(255), cvScalarAll(100), 1);
            // Show it!
            IplImage* contourImage3C = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 100);
            //cvCvtColor(contourImage, contourImage3C, CV_GRAY2BGR);
            cvShowImage("Output", contourImage);
            // We need to pause a little each frame to make sure it doesn't
            // break
            cvWaitKey(10);
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

