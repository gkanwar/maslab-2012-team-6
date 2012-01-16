#include <iostream>

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <opencv/cv.h>
#include <opencv/highgui.h>

using namespace std;

#define colorThreshold 50
#define smoothFrames 2
#define imageWidth 640;
#define imageHeight 480;
class Foo{
public:
        void bar(){
	  bool first = 1;
          IplImage* img = 0;
	  IplImage* past[smoothFrames];
	  for ( int i = 0; i < smoothFrames; i++){
	    past[i]  = cvCreateImage(cvSize(640,480), IPL_DEPTH_8U, 3);
	  }
	  CvCapture* capture = cvCaptureFromCAM( 1);
	  cvNamedWindow("before", CV_WINDOW_AUTOSIZE);
	  cvNamedWindow("after",CV_WINDOW_AUTOSIZE);
	  while (1){
	    img = cvQueryFrame( capture );
	    cvCvtColor(img,img,CV_BGR2HSV);
	    int width = img->width;
	    int height = img->height;
	    int step = img->widthStep;
	    int channels = img->nChannels;

	    uchar *data = (uchar*)img->imageData;
	    for ( int i = 0; i < height; i++ ){
	      for ( int j = 0; j < width; j++ ){
		//		data[ i*step + j*channels+2] = 150;
	      }
	    }
	    cvCvtColor(img,img,CV_HSV2BGR);




	    if ( first == 1 ){
	      first = 0;
	      for (int i = 0; i < smoothFrames; i++ ){
		cvCopy(img,past[i]);
	      }
     	    }
	     
	    cvCopy( img, past[0]);
	    for ( int i = smoothFrames -1; i > 0; i--){
	      cvCopy(past[i-1],past[i]);
	    }
	    cvShowImage("before",img);
	    for ( int i = 0; i < height; i ++ ){
	      for ( int j = 0; j < width; j++ ){
		int index = i*step + j*channels;
		int b = 0,g =0 ,r = 0;
		for ( int k = 0; k < smoothFrames; k++){
		  b += past[k]->imageData[index];
		  g += past[k]->imageData[index+1];
		  r += past[k]->imageData[index+2];
		}
		data[index] = b/smoothFrames;
		data[index+1] = g/smoothFrames;
		data[index+2] = r/smoothFrames;
		if ( data[index]+colorThreshold < data[index+2] 
		     && data[index]+colorThreshold < data[index + 2]
		     && data[index + 2] >= 30){
		  data[index] = 0;
		  data[index+1] = 0;
		  data[index + 2] = 255;
		}
		else{
		  data[index] = 0;
		  data[index + 1] = 0;
		  data[index + 2] = 0;
		}
	      }
	    }
    	    CvMemStorage* storage = cvCreateMemStorage(0);
	    CvSeq* seq = 0;
	    cvPyrSegmentation(img, img, storage, &seq, 5, 200, 50);

	    cvShowImage("after",img);
	    cvWaitKey(10);
	  }
	}
};

extern "C" {
    Foo* Foo_new(){ return new Foo(); }
    void Foo_bar(Foo* foo){ foo->bar(); }
}

