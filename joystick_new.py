import cv2
from PIL import Image
import pygame, pygame.image
import time
from gpiozero import Button
from stepper_new import Stepper
import threading
import copy
from datetime import datetime
import argparse
import time
import json
import os

Game_mode = None
GAME_MODE = None



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
        
        



def main_loop(joystick):
    global GAME_TYPE, Game_mode
    global quit_lock, quit_flag
    keep_running = True
    
    dirPin_x = 2
    stepPin_x = 13
    
    dirPin_y = 3
    stepPin_y = 12
    
    x_stepper = Stepper(stepPin_x,dirPin_x)
    
    y_stepper = Stepper(stepPin_y,dirPin_y)
    
    x_plus_lim = LimitSwitch(4)
    
    x_minus_lim = LimitSwitch(17)
    
    y_plus_lim = LimitSwitch(27)
    
    y_minus_lim = LimitSwitch(22)
    
    
   
    
    imageToBeCaptured = 0
    capture_int_flag = 0

    speed_x = 0
    speed_y = 0
    
    
    # setup shared file for communication with main process
    config = {'space_mode_flag':Game_mode,'image_to_be_captured':imageToBeCaptured ,'correct_postion':0}
    
    
    photo_button_last = 0
    buffer = False
    i =0 
    while keep_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False
            elif event.type == pygame.JOYDEVICEADDED:
                joystick.init()
            elif event.type == pygame.JOYDEVICEREMOVED:
                print("joystick removed")
                raise Exception("Joystick not connected")
                
                
        x = joystick.get_axis(0)
        y = -joystick.get_axis(1)
        mode_button = joystick.get_button(3) # lever_on_bottom
        photo_button = joystick.get_button(0) # first click of red trigger
        capture_int_flag = 0
        

        if GAME_TYPE == 1:
            speed_x = 250*abs(x)**4+500*abs(x)+500
            speed_y = 250*abs(y)**4+500*abs(y)+500
            if (x>0.005)and (x!= 0) and (x_plus_lim.limit_triggered != True): 
                x_stepper.clockwise_inf(speed_x)
    
            elif (x<-0.05) and (x !=0):
                x_stepper.anticlockwise_inf(speed_x)
            
            elif (y>0.005)and (y!= 0):             
                    y_stepper.clockwise_inf(speed_y)
    
            elif (y<-0.005) and (y !=0):
                    y_stepper.anticlockwise_inf(speed_x)
                    
                
            else:
                x_stepper.stop()
            
        elif GAME_TYPE == 0:
            limit_low = 300
            limit_high = 1900
            if x>0:
                speed_x +=0.05
                
            elif x<0:
                speed_x -= 0.05
            elif y<0:
                speed_y -= 0.05
            elif y>0 :
                speed_y += 0.05
            
            speed_x = min(speed_x, limit_high)
            speed_x = max(speed_x, -limit_high)
            speed_y = min(speed_y, limit_high)
            speed_y = max(speed_y,-limit_high)
            
            if (speed_x> limit_low):
                if x_plus_lim.limit_triggered != False:
                    x_stepper.stop()
                else:
                    x_stepper.clockwise_inf(speed_x)
            elif speed_x<-limit_low:
                x_stepper.anticlockwise_inf(abs(speed_x))
            elif (speed_x>-limit_low) and (speed_x < limit_low):
                x_stepper.stop()
        
                
        if (mode_button != 0) and (buffer == False):
            speed_x = speed_y = 0
            
            GAME_TYPE = int(not GAME_TYPE)
            if GAME_TYPE == 1: 
                Game_mode = 'ground'
            else:
                Game_mode = 'space'
            buffer = True
            i = 0


        if (photo_button_last != photo_button) and (buffer == False):
            buffer = True
            photo_button_last = photo_button
            i = 0
            imageToBeCaptured += 1
            
            if imageToBeCaptured >= 2:
                
                capture_int_flag = 1
                imageToBeCaptured = 0

        i += 2
        if i >= 10000:
            buffer = False
        
        print([GAME_TYPE,capture_int_flag ,x])
        
if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("GAME_TYPE", type=int,help="Seconds the game will run for")
    args = argument_parser.parse_args()
    
    GAME_TYPE = args.GAME_TYPE
    if GAME_TYPE == 1:
        Game_mode = "ground"
    else:
        Game_mode = "space"
    pygame.init()
    pygame.joystick.init()
    main_loop((pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None))
    pygame.quit()
    
    
    
    
    