import cv2
from PIL import Image
import pygame, pygame.image
import pygame.camera
import time
from gpiozero import Button
from stepper import Stepper
import threading
import copy
from datetime import datetime
import argparse
import numpy as np
import subprocess
import threading
import sys
import queue
import os
import signal
import json
import RPi.GPIO as GPIO
import threading
import ast
import numpy as np
global BLACK, WHITE, RED, screen_height, screen_width
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)



# Define global variables
quit_lock = threading.Lock()
quit_flag = False
image_buffer = None
image_buffer_lock = threading.Lock()




class ImageReader(threading.Thread):
    def __init__(self, cam):
        super().__init__()
        self.cam = cam

    def run(self) -> None:
        stop = False
        print("Image loop start")
        global quit_lock, quit_flag, image_buffer, image_buffer_lock
        while not stop:
            quit_lock.acquire()
            if quit_flag:
                cam.release()
                stop = True
            quit_lock.release()

            # Read image
            ret, cv_image = self.cam.read()
            if cv_image is not None:
                #img = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                img = cv_image
                # crop the  image
                pixel_crop = 400
                original_image = (640,480)
                crop_x_start = int((original_image[0]-pixel_crop)/2)
                crop_x_end = int(original_image[0]-(original_image[0]-pixel_crop)/2)
                crop_y_start = int((original_image[1]-pixel_crop)/2)
                crop_y_end = int(original_image[1]-(original_image[1]-pixel_crop)/2)
                 
                img = img[crop_x_start:crop_x_end,crop_y_start:crop_y_end]
                buff = cv2.rotate(cv2.convertScaleAbs(cv2.resize(img, [screen_height,screen_width]), 4, -2), cv2.ROTATE_90_COUNTERCLOCKWISE)
                image_buffer_lock.acquire()
                image_buffer = copy.copy(buff)
                image_buffer_lock.release()






def enqueue_output(out, queue):
    for line in iter(out.readline,b''):
        queue.put(line)
    out.close()

def countdown(seconds,screen,font,WIDTH, HEIGHT):
    start_time = pygame.time.get_ticks()
    end_time = start_time + seconds * 1000
    running = True

    while running:
        screen.fill(BLACK)
        current_time = (end_time - pygame.time.get_ticks()) // 1000

        if current_time < 0:
            current_time = 0
            running = False

        text = font.render(str(current_time), True, WHITE)
        text_rect = text.get_rect(center=(HEIGHT // 2, WIDTH // 2))
        screen.blit(text, text_rect)

        pygame.display.flip()


        pygame.time.wait(1000)


def display_init():
    vis_cam = pygame.camera.Camera("/dev/video0",(200,200))
    vis_cam.start()
    screen_info = pygame.display.Info()
    screen_height = screen_info.current_w
    screen_width = screen_info.current_h
    main_display = pygame.display.set_mode((screen_height, screen_width))
    cubesat_logo = pygame.transform.scale(pygame.image.load("figs/logo.png"), (int(0.1 * screen_width) ,int(0.1 * screen_width)) )  
    text = pygame.font.Font("freesansbold.ttf", int(screen_width/10))

    

    return text, [screen_height,screen_width],main_display,vis_cam




def grab_vis_image(vis_cam,main_display):
    vis_image = pygame.transform.rotate(vis_cam.get_image(), 90)
    alpha_val = 128 #100% transparency
    vis_image.set_alpha(alpha_val)
    vis_image = pygame.transform.scale(vis_image, (screen_height, screen_width))
    
    main_display.blit(vis_image, (0,0))




def main_loop(q,text,main_display,threshold):
    
    
    global quit_lock, quit_flag, image_buffer_lock, image_buffer
    points = 0
    ON_POSIX = 'posix' in sys.builtin_module_names
    
    
    
    height, width = screen_height, screen_width

    
    countdown(2, main_display, text, screen_width, screen_height)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False
                
                
        
        
            

        if image_buffer_lock.acquire(timeout=0.001):
            if image_buffer is not None:
                recvsurface = pygame.image.frombuffer(image_buffer.tobytes(), (width, height), 'BGR')
                recvsurface = pygame.transform.rotate(recvsurface, 90)
                recvsurface = pygame.transform.scale(recvsurface, (screen_height, screen_width))
                main_display.blit(recvsurface, (0, 0))
            image_buffer_lock.release()
        
        
        grab_vis_image(vis_cam, main_display)
        pygame.display.flip()
        avg_heat = image_buffer.mean()
        
        
        output = joystick_process.stdout.readline().decode('utf-8')
        output = output[1:-2].split(', ')
        try:
            if output[1] == '1':
                if avg_heat < threshold:
                    points += 1
            if output[0] == '0':
                mode = 'space'
            else:
                mode = 'ground'
        except:
            output = None
        
        
        
        
    quit_lock.acquire()
    quit_flag = True
    quit_lock.release()



def quit_game():
    pygame.quit()


    # begin main loop at kill joystick porcess on keyboard interupt
if __name__ == '__main__':
    
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("countdown_max", type=int,help="Seconds the game will run for")
    argument_parser.add_argument("game_type", type = int, help = "1 for normal, 0 for space")
    args = argument_parser.parse_args()
    COUNTDOWN_TIME = args.countdown_max
    GAME_TYPE = args.game_type
    
    cam = cv2.VideoCapture('/dev/video2')
    pygame.init()
    pygame.camera.init() 
    # pygame.joystick.init()
    
    
    threshold = 50
    
    text, [screen_height,screen_width],main_display,vis_cam = display_init()
    
    image_reader = ImageReader(cam)
    image_reader.start()
    

    joystick_process = subprocess.Popen("python3 joystick_new.py 1", 
                               shell = True,
                               stdin = None,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               bufsize= 1,
                               preexec_fn =os.setsid)
    q = queue.LifoQueue()
    t = threading.Thread(target=enqueue_output,args=(joystick_process.stdout,q))
    while True:
        t.daemon = True
        t.start()
        main_loop(q,text,main_display)
        
        

    

        
        
    
    
    
    
 
            


