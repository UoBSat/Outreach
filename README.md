# Outreach
Code base for UoBSat outreach activities, including "Catch the Volcano!"
Code is divided into 2 major sections:
1) The UI + Camera interface
2) The stepper motor controller interface

## Setup
OS version: Raspbian Buster
Install a little software that emulates thermapp as a vl42 device:
```
sudo apt install libusb-dev libusb-1.0-0-dev
sudo apt install v4l2loopback-dkms
git clone https://github.com/encryptededdy/ThermAppCam.git
cd ThermAppCam/thermapp
```
You need to redefine the video device to be video1, therefore change line 13 in main.c from 

```
#define VIDEO_DEVICE "/dev/video0"
```
to 
```
#define VIDEO_DEVICE "/dev/video1"
```

Here, the makefile is setup for older versions of cmake which like the libraries linked before the file name, but newer versions are unable to find libusb and similar libraries this way. Following the install instructions in the thermapp repo, do:
```
cd thermapp
sudo nano thermapp.h
```
and change the line 
```
#include <libusb>
```
to 
```
#include <libusb-1.0/libusb.h>
```
then
```
make
sudo make install
```
or alternatively
```
gcc -Wall -c -o thermapp.o thermapp.c -lpthread -I/usr/include/libusb-1.0 
gcc thermapp.o main.c -o thermapp -lpthread -lusb-1.0 
```
Now when you do make, it should say thermapp is already setup or similar.
Next:
```
sudo make install
```
Now, whenever you want to read from the thermapp, first connect, keep cap on, then:
```
sudo thermapp
```

Then it can be used as an ordinary webcam with OpenCV.
The following python packages need to be installed via pip:
```
sudo pip install pygame gpiozero threaded pillow numpy queue ast RPi
```
then install opencv for python
```
sudo apt-get install python3-opencv
```
now clone this repository
```
sudo git clone https://github.com/UoBSat/Outreach.git
```


## Start up and Use
### Cable connection
These are the steps for connecting all the necessary cables:
 - Mains power to power supply
 - Mains power to screen
 - HDMI from pi to screen
 - USB from joystick to pi
 - Mains power to pi (pi power adapter), screen shows boot up
 - Pelitier power cables (raw end wires) to crocodile clip cables into channel 2 on power supply (5V 2A)
 - Stepper power calbles (banana cables) to channel 1 on power supply (12V 0.5A)
 - Bind channels (shared ground cable)
 - Turn on power supply (main push switch, then channel 1 and channel 2 buttoms followed by output button)
### Thermal camera (ThermApp)
To start the camera service run the following commands:
```
$ sudo modprobe v4l2loopback
$ sudo thermapp
```
### GUI start
Now leave the thermapp process and open a new terminal and run:

```
$ cd /Outreach
$ python3 main.py XXX Y Z
```
This should then open a pygame window showing the camera feed and you can use the joystick to move the camera. In this command, XXX is replaced with an integer of how long to countdown for. Y is replaced with 1, and Z is replaced with the amount of photos needed. 
