#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <opencv/cv.h>
#include <opencv/highgui.h>

using namespace std;

#define redThreshold 90
#define blueThreshold 30
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
	  CvCapture* capture = cvCaptureFromCAM( 0);
	  cvNamedWindow("before", CV_WINDOW_AUTOSIZE);
	  cvNamedWindow("after",CV_WINDOW_AUTOSIZE);
	  while (1){
	    img = cvLoadImage("/home/ryan/Webcam/2012-01-16-131549.jpg");
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
	    IplImage* ballImage  = cvCreateImage(cvSize(640,480), IPL_DEPTH_8U, 3);
  	    cvCopy(img,ballImage);
	    uchar* redData = (uchar*)ballImage->imageData;
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
		if ( data[index]+redThreshold < data[index+2] 
		     &&data[index+1]+redThreshold < data[index+2]
		     &&data[index+2] >= 30){
		  // ){
		  data[index] = 0;
		  data[index+1] = 0;
		  data[index + 2] = 255;
		  redData[index] = 0;
		  redData[index+1] = 0;
		  redData[index+2] = 255;
		}
	      
		else if ( data[index + 1] + blueThreshold < data[index]
			  && data[index + 2] + blueThreshold < data[index]
			  && data[index] >= 20){
		  redData[index] = 0;
		  redData[index+1] = 0;
		  redData[index+2] = 0;
		  data[index] = 255;
		  data[index + 1] = 0;
		  data[index + 2] = 0;
		  for ( int k = i; k > 0; k-- ){
		    int newIndex = k * step + i * channels;
		    if ( data[newIndex + 1] + blueThreshold < data[index]
			 && data[newIndex + 2] + blueThreshold < data[index]
			 && data[index] >= 20){
		      for ( int l = k; l < i; l++){
			newIndex = l * step + i * channels;
			redData[newIndex] = data[newIndex];
			redData[newIndex+1] = data[newIndex+1];
			redData[newIndex+2] = data[newIndex+2];
		      }
		      break;
		    }
		    else{
		      cout << k << " " << j << endl;
		      redData[newIndex] = 0;
		      redData[newIndex+1] = 255;
		      redData[newIndex+2] = 0;
		    }
		  }
		}
		else{
		  data[index] = 0;
		  data[index+1] = 0;
		  data[index+2] = 0;
		  redData[index] = 0;
		  redData[index+1] = 0;
		  redData[index+2] = 0;
		}
	      }
	    }
	   
    	    CvMemStorage* storage = cvCreateMemStorage(0);
	    CvSeq* seq = 0;
	    cvPyrSegmentation(ballImage, ballImage, storage, &seq, 1, 2,1);
	    int numPieces = seq->total;
	    for ( int i = 0; i < numPieces; i++ ){
	      CvConnectedComp* cc = (CvConnectedComp*) cvGetSeqElem(seq,i);
	      int lineB = 255;
	      int lineG = 255;
	      int lineR = 255;
	      int startX = cc->rect.x;
	      int startY = cc->rect.y;

	      if ( cc->rect.height - 5 < cc->rect.width && cc->rect.height + 5 > cc->rect.width &&
		   cc->rect.height < 250){
		lineG = 0;
		lineR = 0;
	      }

	      for ( int j = 0; j < cc->rect.height; j++){
		for ( int k = 0; k < cc->rect.width; k++){
		  if ( !j || !k || j == cc->rect.height -1 || k == cc->rect.width-1){
		    redData[ (j+startY) * step + (k+startX) * channels ] = lineB;
		    redData[ (j+startY) * step + (k+startX) * channels + 1 ] = lineG;
		    redData[ (j+startY) * step + (k+startX) * channels + 2 ] = lineR;
		  }
		}
	      }	
	    }
	    cvShowImage("after",ballImage);
	    cvWaitKey(10);
	  }
	   
	}
};

extern "C" {
    Foo* Foo_new(){ return new Foo(); }
    void Foo_bar(Foo* foo){ foo->bar(); }
}

