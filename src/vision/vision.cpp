#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <cv.h>
#include <highgui.h>
#include <deque>
using namespace std;

#define CAMERA_NUM 0
#define NUM_FRAMES_TO_AVERAGE 2

#define RED_DISPARITY 100
#define RED_THRESHOLD 60
#define ECCENTRICITY_THRESHOLD 0.1

#define IMG_WIDTH 640
#define IMG_HEIGHT 480

float eccentricity(int w, int h)
{
    float output = abs(float(h-w)/float(h+w));
    cout << "Ecc " << output << endl;
    return output;
}

class ImageProcessing
{
    public:
        // Create some class variables
        CvCapture* capture;
        IplImage* frame;
        IplImage* hsvImage;
        IplImage* normalized;
        IplImage* ballImage;
        IplImage* contourImage;
        IplImage* contourImage3C;
        IplImage* ellipseImage;
        CvMemStorage* contourStorage;
        CvMemStorage* houghStorage;
        CvMemStorage* pointStorage;

        int numFrameCountdown;

        deque<IplImage*> pastFrames;

        ImageProcessing()
        {
            // Create all the images
            frame = cvCreateImage(cvSize(IMG_WIDTH, IMG_HEIGHT), IPL_DEPTH_8U, 3);
            hsvImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            normalized = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            ballImage = cvCreateImage(cvGetSize(normalized), IPL_DEPTH_8U, 1);
            contourImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            contourImage3C = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            ellipseImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);

            // Create a CvMemStorage
            contourStorage = cvCreateMemStorage(0);
            houghStorage = cvCreateMemStorage(0);
            pointStorage = cvCreateMemStorage(0);

            // Set up the capture
            capture = cvCaptureFromCAM(CAMERA_NUM);

            // Make some windows
            cvNamedWindow("Original", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Output", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Intermediate", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Int2", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Ellipse", CV_WINDOW_AUTOSIZE);
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
            cvCvtColor(frame, hsvImage, CV_BGR2HSV);

            for (int i = 0; i < hsvImage->height; i++)
            {
                for (int j = 0; j < hsvImage->width; j++)
                {
                    int index = i * hsvImage->widthStep + j * hsvImage->nChannels;
                    hsvImage->imageData[index+2] = 200;
                }
            }

            cvCvtColor(hsvImage, normalized, CV_HSV2BGR);

            cvShowImage("Int2", normalized);

            // Output hue - REDACTED!
            /*
            IplImage* hueImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            IplImage* satImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            IplImage* valImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            cvSplit(hsvImage, hueImage, satImage, valImage, NULL);
            cvShowImage("Int2", hueImage);
            */

            // Filter the image for red balls
            for (int i = 0; i < normalized->height; i++)
            {
                for (int j = 0; j < normalized->width; j++)
                {
                    int ballImageIndex = i * ballImage->widthStep + j * ballImage->nChannels;
                    int frameIndex = i * normalized->widthStep + j * normalized->nChannels;
                    uchar* imageData = (uchar*) frame->imageData;
                    if (imageData[frameIndex+2] >= imageData[frameIndex] + RED_DISPARITY
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
            CvSeq* contours = NULL;
            cvFindContours(ballImage, contourStorage, &contours);
            // Show it!

            // Process contours with fit ellipse
            int width, height, numPoints;
            cvZero(ellipseImage);
            cvZero(contourImage);
            CvBox2D ellipseBound;
            for (CvSeq* contour = contours; contour != 0; contour = contour->h_next)
            {
                CvSeq* listOfPoints = cvCreateSeq(CV_SEQ_ELTYPE_POINT, sizeof(CvSeq), sizeof(CvPoint), pointStorage);
                numPoints = contour->total;
                if (numPoints <= 20)
                {
                    continue;
                }
                for (int i = 0; i < numPoints; i++)
                {
                    cvSeqPush(listOfPoints, CV_GET_SEQ_ELEM(CvPoint, contour, i));
                }
                ellipseBound = cvFitEllipse2(listOfPoints);
                if (eccentricity(ellipseBound.size.width, ellipseBound.size.height) <= ECCENTRICITY_THRESHOLD)
                {
                    cvEllipse(ellipseImage, cvPoint(ellipseBound.center.x, ellipseBound.center.y), cvSize(ellipseBound.size.width/2, ellipseBound.size.height/2), -ellipseBound.angle, 0, 360, CV_RGB(0, 0xff, 0));
                }
                else
                {
                    cout << "Ecc ellipse" << endl;
                    cvDrawContours(contourImage, contour, CV_RGB(0xff, 0xff, 0xff), CV_RGB(0x99, 0x99, 0x99), -1);
                }
            }
            cvShowImage("Ellipse", contourImage);

            // Process contours with a houghTransform
            CvSeq* houghCircles = cvHoughCircles(contourImage, houghStorage, CV_HOUGH_GRADIENT, 3, 5, 10, 50);
            // Draw them
            for (int i = 0; i < houghCircles->total; i++)
            {
                float* p = (float*) cvGetSeqElem(houghCircles, i);
                CvPoint pt = cvPoint(cvRound(p[0]), cvRound(p[1]));
                cvCircle(ellipseImage, pt, cvRound(p[2]), CV_RGB(0xff, 0, 0));
            }

            cvShowImage("Output", ellipseImage);



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

