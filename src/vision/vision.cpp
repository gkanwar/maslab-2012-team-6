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

#define CAMERA_NUM 1
#define NUM_FRAMES_TO_AVERAGE 2

#define RED_DISPARITY 100
#define RED_THRESHOLD 60
#define ECCENTRICITY_THRESHOLD 0.1
#define YELLOW_FOR_WALL 40

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
        float centerYellowT;
        struct ColorHSV hsvArray[256][256][256];

        //Variable used to test if first run
        int first;

        ImageProcessing()
        {
	    first = 0; 
            // Set up the capture
            capture = cvCaptureFromCAM(CAMERA_NUM);
            // Set up the frame
            largeFrame = cvCreateImage(cvSize(IMG_WIDTH, IMG_HEIGHT), IPL_DEPTH_8U, 3);

            // Create all the images
            frame = cvCreateImage(cvSize(IMG_WIDTH/2, IMG_HEIGHT/2), IPL_DEPTH_8U, 3);
            hsvImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);
            ballImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 1);
            ellipseImage = cvCreateImage(cvGetSize(frame), IPL_DEPTH_8U, 3);

            // Create a CvMemStorage
            contourStorage = cvCreateMemStorage(0);
            houghStorage = cvCreateMemStorage(0);
            pointStorage = cvCreateMemStorage(0);

            // Make some windows
	    // cvNamedWindow("Original", CV_WINDOW_AUTOSIZE);
            //cvNamedWindow("Output", CV_WINDOW_AUTOSIZE);
            //cvNamedWindow("Intermediate", CV_WINDOW_AUTOSIZE);
            //cvNamedWindow("Int2", CV_WINDOW_AUTOSIZE);
            //cvNamedWindow("Ellipse", CV_WINDOW_AUTOSIZE);

            // Load the HSV array from memory
            loadHSVArray();

            pthread_create(&frameCapture, NULL, frameCaptureThread, NULL);
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
        ColorHSV* convertToHSV(uchar b, uchar g, uchar r)
        {
	    return &(hsvArray[r][g][b]);
	}


        void processBalls()
        {
            int index;

            // Shrink the frame, dunno why this "if" is neccessary but it works. 
	    // I also don't know how to spell "necessary" but this works
            if (first == 0)
            {
                 cvZero(largeFrame);
                 first = 1;
            }
            cvPyrDown(largeFrame, frame);

            // Display it
            //cvShowImage("Original", frame);

            // Convert to HSV space
            struct ColorHSV* hsvVal;
            for (int i = 0; i < frame->height; i++)
            {
                for (int j = 0; j < frame->width; j++)
                {
                    index = i * frame->widthStep + j * frame->nChannels;
                    hsvVal = convertToHSV(frame->imageData[index], 
				frame->imageData[index+1], frame->imageData[index+2]);
                    frame->imageData[index] = hsvVal->h;
                    frame->imageData[index+1] = hsvVal->s;
                    frame->imageData[index+2] = hsvVal->v;
                }
            }
            // Filter image using HSV values
            cvZero(ballImage);
	    cvZero(ellipseImage);
            int frameIndex, ballIndex;
	    int numYellow = 0, sumX = 0;
	    uchar hue,sat,val;
            for (int i = 0; i < frame->height; i++)
            {
                for (int j = 0; j < frame->width; j++)
		{
                    frameIndex = i * frame->widthStep + j * frame->nChannels;
                    ballIndex = i * ballImage->widthStep + j * ballImage->nChannels;
		    hue = (uchar)frame->imageData[frameIndex];
		    sat = (uchar)frame->imageData[frameIndex + 1];
		    val = (uchar)frame->imageData[frameIndex + 2];
		    if ( sat <= 255)
		    {
		      if ((hue >= 240 || hue <= 20) && sat >= 100)
		      {
			  ballImage->imageData[ballIndex] = 255;
		      }
		      else if (hue <= 170 && hue >= 150 && sat >= 80)
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
		      else if(hue <= 55 && hue >= 27 && sat >= 55)
		      {
			  sumX += j;
			  numYellow++;
		      }
		    }
                }
            }
	    if(numYellow > YELLOW_FOR_WALL)
	    {
	        float centerYellowX = sumX/numYellow;
		centerYellowT = ((centerYellowX-ballImage->width) - 0.5) * FOV;
	    }
	    else
	    {
	        centerYellowT = -1; 
	    }
	      
	      
	    //cvShowImage("Intermediate",frame);

            // Get contours in the image
            CvSeq* contours = NULL;
            cvFindContours(ballImage, contourStorage, &contours);
            // Process contours with fit ellipse
            int width, height, numPoints;
            float avgCircleR; // Should be D, but whatever
            Ball* tempBall;
            CvBox2D ellBound;
            balls.clear();
            for (CvSeq* contour = contours; contour != 0; contour = contour->h_next)
            {
                CvSeq* listOfPoints = cvCreateSeq(CV_SEQ_ELTYPE_POINT, 
				       sizeof(CvSeq), sizeof(CvPoint), pointStorage);
                numPoints = contour->total;
                if (numPoints <= 20)
                {
                    continue;
                }
                for (int i = 0; i < numPoints; i++)
                {
                    cvSeqPush(listOfPoints, CV_GET_SEQ_ELEM(CvPoint, contour, i));
                }

                ellBound = cvFitEllipse2(listOfPoints);
                cvEllipse(ellipseImage, cvPoint(ellBound.center.x, ellBound.center.y), 
			  cvSize(ellBound.size.width/2, ellBound.size.height/2), 
			  -ellBound.angle, 0, 360, CV_RGB(0, 0xff, 0));

                if (eccentricity(ellBound.size.width, ellBound.size.height) 
		    <= ECCENTRICITY_THRESHOLD)
                {
                    avgCircleR = (ellBound.size.width + ellBound.size.height)/2;
                }
                else
                {
                    avgCircleR = ellBound.size.width < ellBound.size.height ?
                                 ellBound.size.width : ellBound.size.height;
                }
		
                cvEllipse(ellipseImage, cvPoint(ellBound.center.x, ellBound.center.y),
			  cvSize(avgCircleR/2, avgCircleR/2), 
			  - ellBound.angle, 0, 360, CV_RGB(0, 0, 0xff));

                tempBall = (Ball*) new Ball(1000/avgCircleR, 
			        ((ellBound.center.x/ballImage->width) - 0.5) * FOV);
                balls.push_back(tempBall);
            }
            //cvShowImage("Ellipse", ellipseImage);
            cvWaitKey(10);
        }
        int getNumBalls()
        {
            return balls.size();
        }
        float getR(int index)
        {
            return balls[index]->r;
        }
        float getTheta(int index)
        {
            return balls[index]->theta;
        }
        int getYellowCenterT()
        {
            return centerYellowT;
	}
};
//-------------------------------------------------------------------------
//Declaring C functions to interact with python 
//------------------------------------------------------------------------
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
    float getYellowCenterT()
    {
        return ip->getYellowCenterT();
    }
}

