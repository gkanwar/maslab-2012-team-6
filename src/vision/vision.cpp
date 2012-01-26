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
        vector<Ball*> balls;
        bool ranIntoWall;
        struct ColorHSV hsvArray[256][256][256];
        // Declare thresholds
        uchar hHigh;
        uchar hLow;
        uchar sHigh;
        uchar sLow;
	uchar vHigh;
	uchar vLow;
        int i;

        ImageProcessing()
        {
            i = 0;
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
	    hLow = 50;
	    sHigh = 255;
	    sLow = 50;
	    vHigh = 255;
	    vLow = 0;

            // Make some windows
            cvNamedWindow("Original", CV_WINDOW_AUTOSIZE);
            //cvNamedWindow("Output", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Intermediate", CV_WINDOW_AUTOSIZE);
            //cvNamedWindow("Int2", CV_WINDOW_AUTOSIZE);
            cvNamedWindow("Ellipse", CV_WINDOW_AUTOSIZE);

            // Load the HSV array from memory
            loadHSVArray();

            pthread_create(&frameCapture, NULL, frameCaptureThread, NULL);
            ranIntoWall = false;
            cout << "End constructor: " << balls.size() << " " << &balls << endl;
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
                cerr << "File input failed!" << endl;
                return;
            }
	    else
	    {
                cerr << "File input success!" << endl;
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
		    }
		}
	    }
	}
        ColorHSV* convertToHSV( uchar b, uchar g, uchar r )
        {
	    return &(hsvArray[r][g][b]);
	}


        void processBalls()
        {
            cout << "Begin process balls" << endl << flush;
            int index;

            // Shrink the frame
            if (i > 0)
            {
                 cvZero(largeFrame);
                 i--;
            }
            cvPyrDown(largeFrame, frame);

            // Display it
            //cvShowImage("Original", frame);

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

            cout << "Convert to HSV" << endl << flush;
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
            cvSplit(frame, contourImage, NULL, NULL, NULL);
            // Show it
            //cvShowImage("Int2", contourImage);

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

            cout << "Filter image" << endl << flush;
            // Filter image using HSV values
            cvZero(ballImage);
            int frameIndex, ballIndex;
            for (int i = 0; i < frame->height; i++)
            {
                for (int j = 0; j < frame->width; j++)
                {
                    frameIndex = i * frame->widthStep + j * frame->nChannels;
                    ballIndex = i * ballImage->widthStep + j * ballImage->nChannels;
		    uchar hue = (uchar)frame->imageData[frameIndex];
		    uchar sat = (uchar)frame->imageData[frameIndex + 1];
		    uchar val = (uchar)frame->imageData[frameIndex + 2];
                    if ((hue >= 240 || hue <= 20) && sat >= 100 && sat <= 255)
                    {
                        ballImage->imageData[ballIndex] = 255;
                    }
		    else if (hue <= 180 && hue >= 160 && sat >= 80 && sat <= 255)
		    {
		        for (int k = i; k >= 0; k--)
			{
			    index = k*frame->widthStep + j*frame->nChannels;
			    hue = (uchar)frame->imageData[index];
			    sat = (uchar)frame->imageData[index+1];
			    val = (uchar)frame->imageData[index+2];
			    if(hue != 213 || sat != 255 || val != 255)
			    {
			        frame->imageData[index] = 213;
				frame->imageData[index+1] = 255;
				frame->imageData[index+2] = 255;
			    }
			    else
			    {
				break;
			    }
			    
			}
		    }
                }
            }
	    cvShowImage("Intermediate",frame);
            //cvShowImage("Intermediate", ballImage);

            cout << "Find contours" << endl << flush;

            // Get contours in the image
            CvSeq* contours = NULL;
            cvFindContours(ballImage, contourStorage, &contours);//, sizeof(CvContour), CV_RETR_EXTERNAL);
            // Show it!


            cout << "Before process contours" << endl << flush;
            // Process contours with fit ellipse
            int width, height, numPoints;
            float avgCircleR; // Should be D, but whatever
            Ball* tempBall;
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
                    avgCircleR = ellipseBound.size.width < ellipseBound.size.height ?
                                 ellipseBound.size.width : ellipseBound.size.height;
                }
                cvEllipse(ellipseImage, cvPoint(ellipseBound.center.x, ellipseBound.center.y), cvSize(avgCircleR/2, avgCircleR/2), -ellipseBound.angle, 0, 360, CV_RGB(0, 0, 0xff));
                tempBall = (Ball*) new Ball(1000/avgCircleR, ((ellipseBound.center.x/contourImage->width) - 0.5) * FOV);
                balls.push_back(tempBall);
            }
            cvShowImage("Ellipse", ellipseImage);
            cout << "After process contours" << endl << flush;

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

            cvShowImage("Output", ellipseImage);
            */

            // We need to pause a little each frame to make sure it doesn't
            // break
            cvWaitKey(10);
        }
        int getNumBalls()
        {
            cout << "getNumBalls: " << &balls << endl << flush;
            return balls.size();
        }
        float getR(int index)
        {
            cout << "getR" << endl << flush;
            return balls[index]->r;
        }
        float getTheta(int index)
        {
            cout << "getTheta" << endl << flush;
            return balls[index]->theta;
        }
};

extern "C"
{
    ImageProcessing* ip;
    void init()
    {
        ip = new ImageProcessing();
    }
    void deinit()
    {
        delete ip;
    }
    void processBalls()
    {
        ip->processBalls();
    }
    int getNumBalls()
    {
        return ip->getNumBalls();
    }
    float getR(int index)
    {
        return ip->getR(index);
    }
    float getTheta(int index)
    {
        return ip->getTheta(index);
    }
}

