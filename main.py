import cv2
from PIL import Image
import pygame, pygame.image
import time
from gpiozero import Button
from stepper import Stepper
import threading
import copy
from datetime import datetime
import argparse
import time

timeMulti = 0.6

INDEX_X_POS = 0
INDEX_X_NEG = 1
INDEX_Y_POS = 2
INDEX_Y_NEG = 3

LIMIT_SWITCH_PINS = [6,5,19,13]

class LimitSwitch:
    def __init__(self, switch_num):
        self.switch = Button(switch_num)
        self.limit_triggered = False
        self.switch.when_pressed = self.triggered
        self.switch.when_released = self.un_triggered

    def triggered(self):
        self.limit_triggered = True

    def un_triggered(self):
        self.limit_triggered = False

global limit_switches
limit_switches = [LimitSwitch(i) for i in LIMIT_SWITCH_PINS]

global positive_x_limit_reached, negative_x_limit_reached, positive_y_limit_reached, negative_y_limit_reached

def tdelaySpace(x):
    #given an input of a number, calculates time delay between each step of the motor. This is inversely proportional to speed of motor.
    #y = (-1)*timeMulti*(x+1)*(x-1)
    x = abs(x)
    if x == 0:
        x = 0.1
    y = (1/x) * timeMulti - 0.5
    return y

def tdelayNonSpace(x):
    #given an input of a number, calculates time delay between each step of the motor. This is inversely proportional to speed of motor.
    y = (-1)*timeMulti*(x+1)*(x-1)
    return y


def main_loop(joystick):
    global quit_lock, quit_flag
    keep_running = True
    joystick_conn = False
    stepper_1 = Stepper(4,3,2,18)
    stepper_2 = Stepper(20,16,12,7)
    
    tSincex = time.time()
    tSincey = time.time()
    
    spaceMode = True
    previousButton = 0
    
    timeOfLoop = 2.2e-05
    xPrevious = 0
    yPrevious = 0
    
    xVelocity = 0
    yVelocity = 0

    
    while keep_running:
        # Process events first
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False

            elif event.type == pygame.JOYDEVICEADDED:
                print("Joystick connected")
                joystick_conn = True
                joystick.init()
            elif event.type == pygame.JOYDEVICEREMOVED:
                print("joystick removed")
                joystick_conn = False

        if joystick_conn:
            x = joystick.get_axis(0)
            y = -joystick.get_axis(1)
            button = joystick.get_button(4)
        else:
            x = 0.0
            y = 0.0
            button = 0
    
        xPrevious = x
        yPrevious = y
        
        if button == 1:
            if previousButton == 0:
                spaceMode = not spaceMode
                xVelocity = 0
                yVelocity = 0
                
        xVelocity = xVelocity + 100*(0.5 * timeOfLoop * (x + xPrevious))
        yVelocity = yVelocity + 100*(0.5 * timeOfLoop * (y + yPrevious))
                
        if spaceMode == True:
            xdelayReq = tdelaySpace(xVelocity)
            ydelayReq = tdelaySpace(yVelocity)
        else:
            xdelayReq = tdelayNonSpace(x)
            ydelayReq = tdelayNonSpace(y)
        
        if spaceMode == True:
            # Only step steppers beyond a threshold
            if xVelocity > 0 and not limit_switches[INDEX_X_POS].limit_triggered:
                #print(x)
                currentT = time.time()
                if xdelayReq <= (currentT-tSincex):
                    stepper_1.step_clockwise()
                    tSincex = time.time()
                    #print(x)
            elif xVelocity < 0 and not limit_switches[INDEX_X_NEG].limit_triggered:
                #print(x)
                currentT = time.time()
                if xdelayReq <= (currentT-tSincex):
                    stepper_1.step_counterclockwise()
                    tSincex = time.time()
                    #print(x)
            if yVelocity > 0 and not limit_switches[INDEX_Y_POS].limit_triggered:
                #print(y)
                currentT = time.time()
                if ydelayReq <= (currentT-tSincey):
                    stepper_2.step_clockwise()
                    tSincey = time.time()
                    #print(y)
            elif yVelocity < 0 and not limit_switches[INDEX_Y_NEG].limit_triggered:
                #print(y)
                currentT = time.time()
                if ydelayReq <= (currentT-tSincey):
                    stepper_2.step_counterclockwise()
                    tSincey = time.time()
                    #print(y)
        else:
            # Only step steppers beyond a threshold
            if x > 0 and not limit_switches[INDEX_X_POS].limit_triggered:
                #print(x)
                currentT = time.time()
                if xdelayReq <= (currentT-tSincex):
                    stepper_1.step_clockwise()
                    tSincex = time.time()
                    #print(x)
            elif x < 0 and not limit_switches[INDEX_X_NEG].limit_triggered:
                #print(x)
                currentT = time.time()
                if xdelayReq <= (currentT-tSincex):
                    stepper_1.step_counterclockwise()
                    tSincex = time.time()
                    #print(x)
            if y > 0 and not limit_switches[INDEX_Y_POS].limit_triggered:
                #print(y)
                currentT = time.time()
                if ydelayReq <= (currentT-tSincey):
                    stepper_2.step_clockwise()
                    tSincey = time.time()
                    #print(y)
            elif y < 0 and not limit_switches[INDEX_Y_NEG].limit_triggered:
                #print(y)
                currentT = time.time()
                if ydelayReq <= (currentT-tSincey):
                    stepper_2.step_counterclockwise()
                    tSincey = time.time()
                    #print(y)
        
        previousButton = button
        print(x, y, xVelocity, yVelocity)


    print("Exiting control loop")
    quit_lock.acquire()
    quit_flag = True
    quit_lock.release()


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    args = argument_parser.parse_args()

    pygame.init()
    pygame.joystick.init()
    main_loop((pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None))
    pygame.quit()

