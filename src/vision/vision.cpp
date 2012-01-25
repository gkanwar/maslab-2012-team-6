#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <cv.h>
#include <highgui.h>
#include <deque>
#include <pthread.h>
#include <vector>
#include <ctime>

using namespace std;

#define CAMERA_NUM 0
#define NUM_FRAMES_TO_AVERAGE 2

#define RED_DISPARITY 100
#define RED_THRESHOLD 60
#define ECCENTRICITY_THRESHOLD 0.1

#define FOV .907

#define IMG_WIDTH 640
#define IMG_HEIGHT 480

float eccentricity(int w, int h)
{
    float output = abs(float(h-w)/float(h+w));
    return output;
}

// Thread object
pthread_t frameCapture;
// Thread kill received
bool killReceived = false;
// Global variables for image capturing
CvCapture* capture;
IplImage* largeFrame;


// Frame capture thread, constantly queries the frame
void* frameCaptureThread(void* ptr)
{
    cerr << "Frame capture " << clock() << endl;
    // Constantly query frame
    while (!killReceived)
    {
        largeFrame = cvQueryFrame(capture);
    }
    cerr << "End frame capture " << clock() << endl;
}

class Ball
{
    public:
        float r, theta;

        Ball(float tempR, float tempTheta)
        {
            r = tempR;
            theta = tempTheta;
        }
};
struct ColorHSV
{
    uchar h,s,v;
};

class ImageProcessing
{
    public:
        // Declare images
        IplImage* frame;
        IplImage* hsvImage;
        IplImage* normalized;
        IplImage* ballImage;
        IplImage* contourImage;
        IplImage* contourImage3C;
        IplImage* ellipseImage;
        // Declare storages
        CvMemStorage* contourStorage;
        CvMemStorage* houghStorage;
        CvMemStorage* pointStorage;
        // Declare a vector of balls
        vector<Ball> balls;
        bool ranIntoWall;
        struct ColorHSV hsvArray[256][256][256];
        // Declare thresholds
        uchar hHigh;
        uchar hLow;
        uchar sHigh;
        uchar sLow;
	uchar vHigh;
	uchar vLow;

        ImageProcessing()
        {
            // Set up the capture
            capture = cvCaptureFromCAM(CAMERA_NUM);
            // Set up the frame
            largeFrame = cvCreateImage(cvSize(IMG_WIDTH, IMG_HEIGHT), IPL_DEPTH_8U, 3);

            // Create all the images
            frame = cvCreateImage(cvSize(IMG_WIDTH/2, IMG_HEIGHT/2), IPL_DEPTH_8U, 3);
            hsvImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            normalized = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            ballImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            contourImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            contourImage3C = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            ellipseImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);

            // Create a CvMemStorage
            contourStorage = cvCreateMemStorage(0);
            houghStorage = cvCreateMemStorage(0);
            pointStorage = cvCreateMemStorage(0);
	    
	    hHigh = 240;
	    hLow = 20;
	    sHigh = 255;
	    sLow = 100;
	    vHigh = 255;
	    vLow = 0;

            // Make some windows
            cvNamedWindow("Original", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Output", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Intermediate", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Int2", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Ellipse", CV_WINDOW_AUTOSIZE);

            // Load the HSV array from memory
            loadHSVArray();

            pthread_create(&frameCapture, NULL, frameCaptureThread, NULL);
            ranIntoWall = false;
        }

        ~ImageProcessing()
        {
            killReceived = true;
            pthread_join(frameCapture, NULL);
        }

        // HSV conversion functions
        void loadHSVArray()
        {
       	    ifstream hsvFile ("vision/hsvSerial");
            if (!hsvFile)
            {
                cout << "File input failed!" << endl;
                return;
            }
	    else
	    {
	      cout << "File input success!" << endl;
	    }
	    uchar in;
	    for ( int i = 0; i <= 255; i++ )
	    {
		for ( int j = 0; j <= 255; j++ )
		{
		    for ( int k = 0; k <= 255; k++ )
		    {
			hsvArray[i][j][k].h = hsvFile.get();		
			hsvArray[i][j][k].s = hsvFile.get();
			hsvArray[i][j][k].v = hsvFile.get();
                        if (i == 1 && j == 0 && k == 0)
                        {
			  cout << "CHECK0" << (int)hsvArray[i][j][k].h << " " << (int)hsvArray[i][j][k].s << " " <<(int) hsvArray[i][j][k].v << endl;
                        }
		    }
		}
	    }

            cout << "HSV array loaded" << endl;
	}
        ColorHSV* convertToHSV( uchar b, uchar g, uchar r )
        {
	    return &(hsvArray[r][g][b]);
	}


        void processBalls()
        {
            int index;

            cout << "Process balls " << clock() << endl;

            // Shrink the frame
            cvPyrDown(largeFrame, frame);

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
            */

            // Convert to HSV space
            struct ColorHSV* hsvVal;
            for (int i = 0; i < frame->height; i++)
            {
                for (int j = 0; j < frame->width; j++)
                {
                    index = i * frame->widthStep + j * frame->nChannels;
                    hsvVal = convertToHSV(frame->imageData[index], frame->imageData[index+1], frame->imageData[index+2]);
                    frame->imageData[index] = hsvVal->h;
                    frame->imageData[index+1] = hsvVal->s;
                    frame->imageData[index+2] = hsvVal->v;
                }
            }
            cout << "CHECK" << convertToHSV(255, 0, 0)->h << " " << convertToHSV(255, 0, 0)->s << " " << convertToHSV(255, 0, 0)->v << endl;
            cvSplit(frame, NULL, NULL, contourImage, NULL);
            // Show it
            cvShowImage("Int2", contourImage);

            // Output hue - REDACTED!
            /*
            IplImage* hueImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            IplImage* satImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            IplImage* valImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            cvSplit(hsvImage, hueImage, satImage, valImage, NULL);
            cvShowImage("Int2", hueImage);
            */

            // Filter the image for red balls using BGR - REDACTED!
            /*
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
            */

            // Filter image using HSV values
            cvZero(ballImage);
            for (int i = 0; i < hsvImage->height; i++)
            {
                for (int j = 0; j < hsvImage->width; j++)
                {
                    index = i * hsvImage->widthStep + j * hsvImage->nChannels;
                    if (hsvImage->imageData[index] > hLow &&
                        hsvImage->imageData[index] < hHigh &&
                        hsvImage->imageData[index+1] > sLow &&
                        hsvImage->imageData[index+1] < sHigh &&
                        hsvImage->imageData[index+2] > vLow &&
                        hsvImage->imageData[index+2] < vLow)
                    {
                        ballImage->imageData[index] = 255;
                    }
                }
            }


            cout << "After filtering " << clock() << endl;
            cvShowImage("Intermediate", ballImage);


            // Get contours in the image
            CvSeq* contours = NULL;
            cvFindContours(ballImage, contourStorage, &contours, sizeof(CvContour), CV_RETR_EXTERNAL);
            // Show it!
            cout << "After finding contours " << clock() << endl;

            // Process contours with fit ellipse
            int width, height, numPoints;
            float avgCircleR; // Should be D, but whatever
            cvZero(ellipseImage);
            cvZero(contourImage);
            CvBox2D ellipseBound;
            balls.clear();
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
                cvEllipse(ellipseImage, cvPoint(ellipseBound.center.x, ellipseBound.center.y), cvSize(ellipseBound.size.width/2, ellipseBound.size.height/2), -ellipseBound.angle, 0, 360, CV_RGB(0, 0xff, 0));
                if (eccentricity(ellipseBound.size.width, ellipseBound.size.height) <= ECCENTRICITY_THRESHOLD)
                {
                    avgCircleR = (ellipseBound.size.width + ellipseBound.size.height)/2;
                }
                else
                {
                    avgCircleR = ellipseBound.size.width > ellipseBound.size.height ?
                                 ellipseBound.size.width : ellipseBound.size.height;
                }
                cvEllipse(ellipseImage, cvPoint(ellipseBound.center.x, ellipseBound.center.y), cvSize(avgCircleR/2, avgCircleR/2), -ellipseBound.angle, 0, 360, CV_RGB(0, 0, 0xff));
                balls.push_back(Ball(1000/avgCircleR, ((ellipseBound.center.x/contourImage->width) - 0.5) * FOV));
            }
            cvShowImage("Ellipse", contourImage);

            cout << "After ellipse processing " << clock() << endl;

            // Process contours with a houghTransform - REDACTED!
            /*
            CvSeq* houghCircles = cvHoughCircles(contourImage, houghStorage, CV_HOUGH_GRADIENT, 3, 5, 10, 50);
            // Draw them
            for (int i = 0; i < houghCircles->total; i++)
            {
                float* p = (float*) cvGetSeqElem(houghCircles, i);
                CvPoint pt = cvPoint(cvRound(p[0]), cvRound(p[1]));
                cvCircle(ellipseImage, pt, cvRound(p[2]), CV_RGB(0xff, 0, 0));
            }

            cout << "After hough processing " << clock() << endl;

            cvShowImage("Output", ellipseImage);
            */

            // We need to pause a little each frame to make sure it doesn't
            // break
            cvWaitKey(10);
            cout << "End process balls " << clock() << endl;
        }
        int getNumBalls()
        {
            return balls.size();
        }
        float getR(int index)
        {
            return balls[index].r;
        }
        float getTheta(int index)
        {
            return balls[index].theta;
        }
};

extern "C"
{
    ImageProcessing* createObj()
    {
        return new ImageProcessing();
    }
    void deleteObj(ImageProcessing* ip)
    {
        delete ip;
    }
    void processBalls(ImageProcessing* ip)
    {
        ip->processBalls();
    }
    int getNumBalls(ImageProcessing* ip)
    {
        return ip->getNumBalls();
    }
    float getR(ImageProcessing* ip, int index)
    {
        return ip->getR(index);
    }
    float getTheta(ImageProcessing* ip, int index)
    {
        return ip->getTheta(index);
    }
}

