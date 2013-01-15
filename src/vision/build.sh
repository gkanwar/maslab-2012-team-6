#! /bin/bash

filename=vision.cpp
libname=libvision.so

g++ -I/usr/include/opencv -c -fPIC $filename -o temp.o
g++ -shared -Wl,-soname,$libname -o $libname  temp.o -lopencv_core -lopencv_highgui -lpthread
rm temp.o
