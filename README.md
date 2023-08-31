# Outreach
Code base for UoBSat outreach activities, including "Catch the Volcano!"
Code is divided into 2 major sections:
1) The UI + Camera interface
2) The stepper motor controller interface

## Setup
### Thermal Camera
Install a little software that emulates thermapp as a vl42 device:
```
$ sudo apt install libusb-dev libusb-1.0-0-dev
$ sudo apt install v4l2loopback-dkms
$ git clone https://github.com/encryptededdy/ThermAppCam.git
$ cd ThermAppCam/thermapp
```

Here, the makefile is setup for older versions of cmake which like the libraries linked before the file name, but newer versions are unable to find libusb and similar libraries this way. So our best bet is to write the gcc commands ourselves since there are only 3 files instead of wasting time otherwise.
```
$ gcc -Wall -c -o thermapp.o thermapp.c -I/usr/include/libusb-1.0 -lpthread
$ gcc thermapp.o main.o   -o thermapp -lusb-1.0 -lpthread
```

Now when you do make, it should say thermapp is already setup or similar.
Next:
```
$ sudo make install
```
Now, whenever you want to read from the thermapp, first connect, keep cap on, then:
```
$ sudo thermapp
```

Then it can be used as an ordinary webcam with OpenCV. There will be a script to automate this and launch...somewhere....
### Pin Initialization
On the startup, the Pi's GPIO pins need to be set to low (not floating). To do this a service need to be setup on the PI that pulls the pins low on start up. This involves three files:
- pinsetup.py
- pinsteup.sh
- pintsetup.service

Follow the instructions here to setup this up:
https://www.instructables.com/Raspberry-Pi-Launch-Python-script-on-startup/

## Start up and Use
### Thermal camera (ThermApp)
IF YOU WANT TO RUN THE CAMERA SEPERATELY, run the following commands (else skip this and run the main.py python file as below):
```
$ sudo modprobe v4l2loopback
$ sudo thermapp
```
Now leave this process and open a new terminal and run, this is the core programme of the entire game:

```
$ cd /Outreach
$ python3 main.py XXX
```
This should then open a pygame window showing the camera feed and you can use the joystick to move the camera. In this command, XXX is replaced with an integer of how long to countdown for.

### Volcano Peltiers
The peltiers should be run at SOMEHTING A and SOMETHING V off the 4 in 1 relay board on the rig. The peltier_control.py file us used to randomly switch these on and off and is started by the main.py script.