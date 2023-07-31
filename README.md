# Outreach
Code base for UoBSat outreach activities, including "Catch the Volcano!"
Code is divided into 2 major sections:
1) The UI + Camera interface
2) The stepper motor controller interface

## Setup
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

## Start up and Use
### Thermal camera (ThermApp)
To start the camera service run the following commands:
```
$ sudo modprobe v4l2loopback
$ sudo thermapp
```
Now leave this process and open a new terminal and run:

```
$ cd /Outreach
$ python3 main.py
```
This should then open a pygame window showing the camera feed and you can use the joystick to move the camera.
