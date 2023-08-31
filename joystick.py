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
import json

timeMulti = 0.6

INDEX_X_POS = 0
INDEX_X_NEG = 1
INDEX_Y_POS = 2
INDEX_Y_NEG = 3

LIMIT_SWITCH_PINS = [23,24,8,25]

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


def tdelaySpace(speed) -> float:
    """
    Given an input of a number, calculates time delay between each step of the motor. This is inversely proportional to speed of motor.

    :param speed: Speed of the steppers in rotation per second
    :returns: Delay between each step of the stepper motor in seconds.
    """

    speed = abs(speed)
    if speed == 0:
        speed = 0.1
    y = (1/(speed * 0.01)) * timeMulti - 0.15 # Offsetting the time curve towards 0, use it to change sensitivity of joystick( increase it for more)
    return y

def tdelayNonSpace(x):
    #given an input of a number, calculates time delay between each step of the motor. This is inversely proportional to speed of motor.
    y = (-1)*timeMulti*(x+1)*(x-1)
    return y

def start_routine():
    #finding x axis
    stepper_1 = Stepper(4,3,2,17) 
    stepper_2 = Stepper(20,16,12,7)
    gantry_max_coords = (0, 0)
    while not limit_switches[INDEX_X_POS].limit_triggered:
        stepper_2.step_clockwise()
    #print('done x pos')
    while not limit_switches[INDEX_X_NEG].limit_triggered:
        stepper_2.step_counterclockwise()
        gantry_max_coords = (gantry_max_coords[0] + 1, gantry_max_coords[1])
    #print('done x neg')
    #finding y axis
    while not limit_switches[INDEX_Y_POS].limit_triggered:
        stepper_1.step_counterclockwise()
    #print('done y pos')
    while not limit_switches[INDEX_Y_NEG].limit_triggered:
        stepper_1.step_clockwise()
        gantry_max_coords = (gantry_max_coords[0] , gantry_max_coords[1] + 1)
    #print('done y neg')
        
    #moves gantry away from edge of board
    for i in range(200):
        stepper_2.step_clockwise()
    for i in range(200):
        stepper_1.step_counterclockwise()
    return gantry_max_coords
    

def main_loop(joystick):
    
    """#verifying coordinates
    gantry_max_coords = start_routine()
    #print(gantry_max_coords)
    dictionary = {
        "gantry_max_x" : gantry_max_coords[0],
        "gantry_max_y" : gantry_max_coords[1]
    }
    with open("config.json", "w") as outfile:
        json.dump(dictionary, outfile)
    gantry_coords = (200, 200)"""
    
    global quit_lock, quit_flag
    keep_running = True
    joystick_conn = False
    stepper_1 = Stepper(4,3,2,17)
    stepper_2 = Stepper(20,16,12,7)
    
    tSincex = time.time()
    tSincey = time.time()
    
    spaceMode = False
    imageToBeCaptured = False
    correctPostion = False
    mode_int_flag = 0
    correct_int_flag = 0
    capture_int_flag = 0
    
    previous_photo_button = 0
    previous_mode_button = 0
    
    timeOfLoop = 1e-10 # Arbitrary initial value
    initial_time = time.time()

    xPrevious = 0
    yPrevious = 0
    
    xVelocity = 0
    yVelocity = 0

    # printing initial values of joystick status
    print([mode_int_flag,capture_int_flag ,correct_int_flag])
    
    # setup shared file for communication with main process
    config = {'space_mode_flag':spaceMode,'image_to_be_captured':imageToBeCaptured ,'correct_postion':correctPostion}
    
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
            mode_button = joystick.get_button(4) # grey button on the side
            photo_button = joystick.get_button(0) # first click of red trigger
        else:
            x = 0.0
            y = 0.0
            mode_button = 0
            photo_button = 0
    
        
        if mode_button == 1:
            if previous_mode_button == 0:
                #change joystick control type
                spaceMode = not spaceMode
                if spaceMode == 1:
                    mode_int_flag = 1
                else:
                    mode_int_flag = 0
                #config['space_mode_flag'] = spaceMode
                # log to config file current joy stick related state
                #with open('config.json','w') as configFile:
                #    json.dump(config,configFile)
                #    configFile.close()
                xVelocity = 0
                yVelocity = 0
            print([mode_int_flag,capture_int_flag ,correct_int_flag])
        if photo_button == 1:
            if previous_photo_button == 0:
                #photo capture event
                imageToBeCaptured = not imageToBeCaptured
                if imageToBeCaptured == True:
                    capture_int_flag = 1
                else:
                    capture_int_flag = 0
            print([mode_int_flag,capture_int_flag ,correct_int_flag])

                #config['image_to_be_captured'] = imageToBeCaptured
                # log to config file current joy stick related state
                #with open('config.json','w') as configFile:
                #    json.dump(config,configFile)
                #    configFile.close()
        # Here raw x and y are considered accelerations
        xVelocity = xVelocity + 100*(0.5 * timeOfLoop * (x + xPrevious))
        yVelocity = yVelocity + 100*(0.5 * timeOfLoop * (y + yPrevious))
        

        if xVelocity > 530:
            xVelocity = 530
        elif xVelocity < -530:
            xVelocity = -530
        if yVelocity > 530:
            yVelocity = 530
        elif yVelocity < -530:
            yVelocity = -530
        
        #print (xVelocity, yVelocity)

        xPrevious = x
        yPrevious = y

        x_inp = 0
        y_inp = 0
        
        if spaceMode == True:
            xdelayReq = tdelaySpace(xVelocity)
            ydelayReq = tdelaySpace(yVelocity)
            x_inp = xVelocity
            y_inp = yVelocity
        else:
            xdelayReq = tdelayNonSpace(x)
            ydelayReq = tdelayNonSpace(y)
            x_inp = x
            y_inp = y
        
        currentT = time.time()
        if x_inp > 0 and not limit_switches[INDEX_X_POS].limit_triggered:
            if xdelayReq <= (currentT-tSincex):
                stepper_2.step_clockwise()
                #gantry_max_coords = (gantry_coords[0] + 1, gantry_coords[1])
                tSincex = currentT
                #print(x_inp)
        elif x_inp < 0 and not limit_switches[INDEX_X_NEG].limit_triggered:
            if xdelayReq <= (currentT-tSincex):
                stepper_2.step_counterclockwise()
                #gantry_max_coords = (gantry_coords[0] - 1, gantry_coords[1])
                tSincex = currentT
                #print(x_inp)
        if y_inp > 0 and not limit_switches[INDEX_Y_POS].limit_triggered:
            if ydelayReq <= (currentT-tSincey):
                stepper_1.step_counterclockwise()
                #gantry_max_coords = (gantry_coords[0], gantry_coords[1] + 1)
                tSincey = currentT
                #print(y_inp)
        elif y_inp < 0 and not limit_switches[INDEX_Y_NEG].limit_triggered:
            if ydelayReq <= (currentT-tSincey):
                stepper_1.step_clockwise()
                #gantry_max_coords = (gantry_coords[0], gantry_coords[1] - 1)
                tSincey = currentT
                #print(y_inp)

        
        
        previous_mode_button = mode_button
        previous_photo_button  = photo_button
        #print(x, y, xVelocity, yVelocity)
        
        timeOfLoop = currentT - initial_time
        initial_time = currentT
        

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
