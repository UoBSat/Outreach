import cv2
from PIL import Image
import pygame, pygame.image
from pygame.locals import *
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

global BLACK, WHITE, RED, CROSSHAIR
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
CROSSHAIR = (52, 140, 25)
GREY = (128,128,128)

# Define global variables
quit_lock = threading.Lock()
quit_flag = False
image_buffer = None
image_buffer_lock = threading.Lock()

def enqueue_output(out, queue):
    for line in iter(out.readline,b''):
        queue.put(line)
    out.close()


def draw_rect(colour, x, y, width, height, rad):
    
    width_show = width*screen_width
    height_show = screen_width*height
    aspect = screen_width/screen_height
    rect = Rect(0, 0, width_show, height_show, border_radius = rad)
    
    rect.centerx = (x+(-x+0.5)*width)*screen_width
    rect.centery = (1-(y+(-y+0.5)*(width*aspect)))*screen_height
    pygame.draw.rect(main_display, colour, rect)
    
    
def draw_poly(colour, points):
    for i in points:
        i[0] *= screen_width
        i[1] = (1-i[1])*screen_height
        

    
    x = pygame.draw.polygon(main_display, colour, points)
    return x

def draw_line(color, p1, p2, width_):
    pygame.draw.line(main_display, color, (p1[0]*screen_width, (1-p1[1])*screen_height), (p2[0]*screen_width, (1-p2[1])*screen_height), width=width_)

def draw_circle(center, radius, colour, sides=64):
    points = [
        [center[0] + radius * np.cos(np.deg2rad(angle)),
         center[1] + radius * np.sin(np.deg2rad(angle))]
        for angle in range(0, 360, 360 // sides)
    ]
    draw_poly(colour, points)

def make_UI(screen,photo_points,mode,font,time_left,score):
    #Crosshair 
    
    # draw_rect(CROSSHAIR, 0.75, 0.59, 0.01, 0.075, 1)
    # draw_rect(CROSSHAIR, 0.75, 0.59, 0.075, 0.01, 1)
    pygame.draw.circle(screen, CROSSHAIR, (0.76*screen_width,(1-0.55)*screen_height), 0.2*screen_width*0.1)
    
    
    
    #staging stuff
    stage_width = 0.1
    stage_height = 0.05
    stage_x = 0  # Moved to the left
    stage_spacing = 0.09  # Reduced spacing
    top_box_stage = (1-(0.1+photo_points * stage_spacing+0.05))*screen_height
    right_box_stage = 0.175
    top_box_stage = 0.05+(photo_points * stage_spacing)
    
    draw_poly(BLACK, [[0,0],[0,top_box_stage],[right_box_stage,top_box_stage],[right_box_stage,0]])
    for i in range(photo_points):
        stage_y = 0.1+i * stage_spacing
        stage_points = [
            [stage_x, stage_y],
            [stage_x + stage_width, stage_y],
            [stage_x + stage_width, stage_y - stage_height],
            [stage_x, stage_y - stage_height]
        ]
        box = draw_poly(WHITE, stage_points)
        square_center = [(stage_x+stage_width/2)*screen_width,(1-(stage_y-stage_height/2))*screen_height]
        stage_text = font.render(str(i+1), True, RED)
        stage_text_rect = stage_text.get_rect(center=(square_center[0],square_center[1]))
        screen.blit(stage_text, stage_text_rect)
    
    photo_text = font.render("Photos left", True, WHITE)
    photo_text_rect = stage_text.get_rect(center=(0.01*screen_width,(1-(0.1+i * stage_spacing+0.015))*screen_height))
    screen.blit(photo_text, photo_text_rect)
    

    
    
    
    
    
    
    # Drawing the Altimeter Needle
    draw_poly(WHITE, [[0.35,1],[0.35,0.9],[0.65,0.9],[0.65,1]])
    altimeter_center = [0.4, 0.95]
    altimeter_radius = 0.05
    draw_circle(altimeter_center, altimeter_radius, GREY)
    needle_length = altimeter_radius * 0.9
    needle_angle = ((time_left/COUNTDOWN_TIME)*360)+90
    needle_points = [
        altimeter_center,
        [altimeter_center[0] + needle_length *np.cos(np.deg2rad(needle_angle)),
         altimeter_center[1] + needle_length * np.sin(np.deg2rad(needle_angle))]
    ]
    draw_line(RED, needle_points[0],needle_points[1],10)
    font = pygame.font.Font(None, int(screen_width/15))
    time_text = font.render(str(round(time_left,0)),True,BLACK)
    
    time_text_rect = stage_text.get_rect(center=(0.55*screen_width,(1-0.96)*screen_height))
    screen.blit(time_text,time_text_rect)
    
    
    #mode and score 
    
    draw_poly(BLACK, [[0.5,0],[0.5,0.05],[1,0.05],[1,0]])
    font = pygame.font.Font(None, int(screen_width/25))

    mode_text = font.render(f"Mode: {mode}",True,WHITE)
    mode_text_box = stage_text.get_rect(center=(0.52*screen_width,(0.97*screen_height)))
    screen.blit(mode_text,mode_text_box)
    
    
    

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
                IMAGE_SIZE = (1000,1000)
                img = img[crop_x_start:crop_x_end,crop_y_start:crop_y_end]
                buff = cv2.rotate(cv2.convertScaleAbs(cv2.resize(img, IMAGE_SIZE), 4, -2), cv2.ROTATE_90_COUNTERCLOCKWISE)
                image_buffer_lock.acquire()
                image_buffer = copy.copy(buff)
                image_buffer_lock.release()
                
                
                
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
    global screen_width, screen_height, main_display
    vis_cam = pygame.camera.Camera("/dev/video0",(200,200))
    vis_cam.start()
    screen_info = pygame.display.Info()
    screen_height = screen_info.current_h
    screen_width = screen_info.current_w
    # screen_width -= screen_width/100
    screen_height -= screen_height*0.1
    main_display = pygame.display.set_mode((screen_width, screen_height))
    cubesat_logo = pygame.transform.scale(pygame.image.load("figs/logo.png"), (int(0.1 * screen_width) ,int(0.1 * screen_width)) )  
    text = pygame.font.Font("freesansbold.ttf", int(screen_width/10))
    
    
    
    
    
    

    

    return text, [screen_height,screen_width],main_display,vis_cam

def grab_vis_image(vis_cam,main_display):
    vis_image = pygame.transform.rotate(vis_cam.get_image(), 90)
    alpha_val = 128 #100% transparency
    vis_image.set_alpha(alpha_val)
    vis_image = pygame.transform.scale(vis_image, (screen_width, screen_height))
    
    main_display.blit(vis_image, (0,0))

def main_loop(q,text,main_display,time_left,photos_left):
    
    global quit_lock, quit_flag, image_buffer_lock, image_buffer
    
    ON_POSIX = 'posix' in sys.builtin_module_names
    
    
    start_time = pygame.time.get_ticks()
    end_time = start_time + time_left * 1000
    font = pygame.font.Font(None, int(screen_width/30))
    height, width = screen_height, screen_width
    take_photo = None
    take_photo_last = take_photo
    mode = 'init'
    time_left = 10000
    countdown(10, main_display, text, screen_width, screen_height)
    score = 0
    print("here")
    while (time_left> 0) and (photos_left> 0):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False
                
        time_left = (end_time - pygame.time.get_ticks()) // 1000
        output = joystick_process.stdout.readline().decode('utf-8')
        output = output[1:-2].split(', ')

        
            
        IMAGE_SIZE = (1000,1000)
        IMAGE_DISPLAY_LOCATION = (-(IMAGE_SIZE[1]-screen_width)/2-200, -(IMAGE_SIZE[0]-screen_height)/2)
        # IMAGE_DISPLAY_LOCATION = (screen_width,screen_height)
        if image_buffer_lock.acquire(timeout=0.001):
            if image_buffer is not None:
                # Convert opencv image to pygame compatible image
                #print('found image in buffer')
                recvsurface = pygame.image.frombuffer(image_buffer, IMAGE_SIZE[::-1], 'BGR')
                recvsurface = pygame.transform.scale(recvsurface, ((screen_width,screen_height)))
                recvsurface = pygame.transform.rotate(recvsurface, 180)
                main_display.blit(recvsurface, (0,0))
            image_buffer_lock.release()
        
        
        grab_vis_image(vis_cam, main_display)
        make_UI(main_display,photos_left,mode,font,time_left,score)
        pygame.display.flip()
        avg_heat = image_buffer.mean()
        
        
        
        try:
            if output[0] == '1':
                None
        except:
            output = None
        if (output != None) and (len(output) == 2):
            if ((output[1] == '0') or (output[1] == '1')):
                take_photo = output[1]
                if (take_photo != take_photo_last) and (take_photo_last != None):
                    
                    photos_left -= 1
                    if avg_heat < 50:
                        score += 1
                take_photo_last =take_photo
            if (output[0] == '0'):
                mode = 'space'
            elif (output[0] == '1'):
                mode = 'ground'
            else:
                None
            print("Here1")
        
    quit_lock.acquire()
    quit_flag = True
    quit_lock.release()
    
    return score

def quit_game():
    pygame.quit()

if __name__ == '__main__':
    global COUNTDOWN_TIME
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("countdown_max", type=int,help="Seconds the game will run for")
    argument_parser.add_argument("game_type", type = int, help = "1 for normal, 0 for space")
    argument_parser.add_argument("photos", type = int, help = "how many photos does the player get?")
    args = argument_parser.parse_args()
    COUNTDOWN_TIME = args.countdown_max
    GAME_TYPE = args.game_type
    PHOTOS_LEFT = args.photos
    
    cam = cv2.VideoCapture('/dev/video2')
    pygame.init()
    pygame.camera.init() 
    # pygame.joystick.init()
    
    text, [screen_height,screen_width],main_display,vis_cam = display_init()
    
    image_reader = ImageReader(cam)
    image_reader.start()
    

    joystick_process = subprocess.Popen(f"python3 joystick.py {GAME_TYPE}", 
                               shell = True,
                               stdin = None,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               bufsize= 1,
                               preexec_fn =os.setsid)
    q = queue.LifoQueue()
    t = threading.Thread(target=enqueue_output,args=(joystick_process.stdout,q))
    
    t.daemon = True
    t.start()
    score = main_loop(q,text,main_display,COUNTDOWN_TIME,PHOTOS_LEFT)
    
    
    print(score)
    
    time.sleep(2)
        

    

        
        
    
    
    
    
 
            


