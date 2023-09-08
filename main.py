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

cubesat_size = (155, 155)
cubesat_logo = pygame.image.load("figs/logo.png")
cubesat_logo = pygame.transform.scale(cubesat_logo, cubesat_size)
cubesat_location = (-10, 844)

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 1000
IMAGE_SIZE = (1000,1000)
IMAGE_DISPLAY_LOCATION = (-(IMAGE_SIZE[1]-DISPLAY_WIDTH)/2, -(IMAGE_SIZE[0]-DISPLAY_HEIGHT)/2)

static_screen = pygame.image.load("figs/static.gif")
static_screen = pygame.transform.scale(static_screen, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
static_screen_location = (0, 0)

MODE_TYPE = ("Ground", "Space")

FONT_COLOR_GREEN = (0, 150, 0)
FONT_COLOR_WHITE = (255, 255, 255)
FONT_COLOR_RED = (150, 0, 0)

GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GREY = (40, 40, 40)
LIGHT_GREY = (120, 120, 120)

CROSSHAIR_COLOR = (40, 40, 40)
BACKGROUND_COLOR = (250, 0, 0)
crosshair_width = 1
crosshair_length = 150

COUNTDOWN_DISPLAY_LOCATION = (703, 937)
COUNTDOWN_BAR_WIDTH = 5
COUNTDOWN_AREA_WIDTH = 302
NUM_OF_BARS = 100 #use 50 to keep green bars seperated 

LIMIT_SWITCH_PINS = [6,5,19,13]

global image_buffer, image_buffer_lock, quit_lock, image_available, quit_flag
image_buffer = None
image_buffer_lock = threading.Lock()
quit_lock = threading.Lock()
image_available = False
quit_flag = False

#whether to restart game
restart = True

def enqueue_output(out, queue):
    for line in iter(out.readline,b''):
        queue.put(line)
    out.close()

def draw_rect(colour, x, y, length, height, rad):
        pygame.draw.rect(main_display, colour, (x, y, length, height), border_radius=rad)

def draw_tri(colour, x1, y1, x2, y2, x3, y3):
        pygame.draw.polygon(main_display, colour, [(x1, y1), (x2, y2), (x3, y3)])

def draw_line(color, x1, y1, x2, y2, width_):
    pygame.draw.line(main_display, color, (x1, y1), (x2, y2), width=width_)
        
def visual_countdown(total_time, time_remaining):
    if time_remaining == 0:
        return 0
    else:
        BAR_GAP = (COUNTDOWN_AREA_WIDTH - NUM_OF_BARS * COUNTDOWN_BAR_WIDTH)/(NUM_OF_BARS - 1)
        time_elapsed = (total_time - time_remaining)
        time_per_bar = total_time/NUM_OF_BARS
        NUM_BARS_TO_DRAW = int(NUM_OF_BARS - (time_elapsed//time_per_bar))
        for i in range(NUM_BARS_TO_DRAW):
            #x and y coord start at the right most spot for the bar and work left
            draw_rect(GREEN, DISPLAY_WIDTH - COUNTDOWN_BAR_WIDTH * (i + 1) - BAR_GAP * i, 929, COUNTDOWN_BAR_WIDTH, 71, 0)
    

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
                img = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
                # crop the image
                pixel_crop = 400
                original_image = (640,480)
                crop_x_start = int((original_image[0]-pixel_crop)/2)
                crop_x_end = int(original_image[0]-(original_image[0]-pixel_crop)/2)
                crop_y_start = int((original_image[1]-pixel_crop)/2)
                crop_y_end = int(original_image[1]-(original_image[1]-pixel_crop)/2)
                 
                img = img[crop_x_start:crop_x_end,crop_y_start:crop_y_end]
                buff = cv2.rotate(cv2.convertScaleAbs(cv2.resize(img, IMAGE_SIZE), 4, -2), cv2.ROTATE_90_COUNTERCLOCKWISE)
                image_buffer_lock.acquire()
                image_buffer = copy.copy(buff)
                image_buffer_lock.release()
        print("Exiting image loop")

def make_text(font_size, input_text, color, x, y):
        text = pygame.font.Font("freesansbold.ttf", font_size)
        message = text.render(input_text, True, color)
        main_display.blit(message, (x, y))

def make_UI(mode_number):
    #main_display.fill(BACKGROUND_COLOR)
    #crosshairs
    draw_line(CROSSHAIR_COLOR, DISPLAY_WIDTH/2, (DISPLAY_HEIGHT/2 - crosshair_length/2), DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2 + (crosshair_length/2), crosshair_width)
    draw_line(CROSSHAIR_COLOR, (DISPLAY_WIDTH/2 - crosshair_length/2), DISPLAY_HEIGHT/2, (DISPLAY_WIDTH/2 + crosshair_length/2), DISPLAY_HEIGHT/2, crosshair_width)

    #brs = bottom right square, tlt = top left triangle etc
    #brt
    draw_tri(GREY, 694, 925, 694, 1000, 644, 1000)
    #bls
    draw_rect(GREY, 0, 850, 150, 150, 0)
    #brr
    draw_rect(GREY, 694, 925, 306, 75, 0)
    #blr
    draw_rect(GREY, 150, 900, 200, 100, 0)
    #blt
    draw_tri(GREY, 350, 900, 350, 1000, 450, 1000)
    #tr
    draw_rect(GREY, 350, 0, 300, 100, 0)
    #tlt
    draw_tri(GREY, 350, 0, 350, 100, 300, 0)
    #trt
    draw_tri(GREY, 650, 0, 650, 100, 700, 0)
    
    #bls
    draw_rect(BLACK, 0, 854, 146, 146, 0)
    #blr
    draw_rect(BLACK, 150, 904, 196, 96, 0)
    #blt
    draw_tri(BLACK, 346, 904, 346, 1000, 445, 1000)
    #tmr
    draw_rect(BLACK, 350, 0, 300, 95, 0)
    #tlt
    draw_tri(BLACK, 350, 0, 350, 95, 305, 0)
    #trt
    draw_tri(BLACK, 650, 0, 650, 95, 695, 0)
    #brr
    draw_rect(BLACK, 698, 929, 302, 77, 0)
    #brt
    draw_tri(BLACK, 698, 929, 698, 1000, 648, 1000)
    
    small_cubesat_logo = pygame.transform.scale(cubesat_logo, (50, 50))
    main_display.blit(cubesat_logo, cubesat_location)
    
    for i in range(photos_left):
        main_display.blit(small_cubesat_logo, (200 + 50 * i, 950))
    
    #main_display.blit(static_screen, static_screen_location)
    
    #lines across the rectangles in the bottom left
    draw_line(GREY, 397, 950, 150, 950, 4)
    draw_line(GREY, 200, 950, 200, 1000, 4)
    
    visual_countdown(COUNTDOWN_TIME, countdown_counter)
    
    make_text(50, str(countdown_counter), (FONT_COLOR_WHITE if countdown_counter > 10 else FONT_COLOR_RED), COUNTDOWN_DISPLAY_LOCATION[0], COUNTDOWN_DISPLAY_LOCATION[1])
    #print(mode_number)
    make_text(40, "Mode: " + MODE_TYPE[mode_number], FONT_COLOR_WHITE, 350, 30)
    make_text(45, str(photos_left), FONT_COLOR_WHITE, 160, 955)
    make_text(25, "Velocity: " + str(velocity), FONT_COLOR_WHITE, 155, 910)

def end_of_game(end_game_type):
    restart_choosing = True
    while restart_choosing == True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                restart = False
                return False
        if end_game_type == "time_fail":
            draw_rect(LIGHT_GREY, 250, 450, 500, 100, 20)
            make_text(40, "Times up!", FONT_COLOR_WHITE, 260, 460)
            make_text(40, "Thanks for playing :)", FONT_COLOR_WHITE, 260, 505)
        elif end_game_type == "photos_fail":
            return 1
        elif end_game_type == "win":
            return 1
        else:
            restart = False
            return restart
        pygame.display.flip()

def clean_up_actions():
    # vis_cam.stop()
    # kill subprocesses
    os.killpg(os.getpgid(joystick_process.pid),signal.SIGTERM)
    os.killpg(os.getpgid(peltier_process.pid),signal.SIGTERM)
    #os.killpg(os.getpgid(thermal_camera_process.pid),signal.SIGTERM)

    # ensure peltiers are turned off
    GPIO.setmode(GPIO.BCM)
    peltiers = [26,19,13,6]
    for peltier in peltiers:
        GPIO.setup(peltier, GPIO.OUT)
        GPIO.output(peltier, 0)

    # ensure stepper pins are low
    GPIOs = [4, 3, 2, 18, 20, 16, 12, 7]

    for gpio in GPIOs:
        GPIO.setup(gpio, GPIO.OUT)
        GPIO.output(gpio, 0)

    quit_flag = True
    pygame.quit()

def main_loop(q):
    global quit_lock, quit_flag, image_buffer_lock, image_buffer
    keep_running = True
    clock = pygame.time.Clock()
    count = 0
    image_saved = True
    last_time = time.time()
    total_time_passed = 0
    
    global countdown_counter, photos_left, velocity
    countdown_counter = COUNTDOWN_TIME
    photos_left = 4
    velocity = 3.9
    show_time_up = False

    #defines the objects in the line printed from joystick that represents if a photo_taken request was sent in the previous line
    previous_line_element_2 = 0

    # magic
    ON_POSIX = 'posix' in sys.builtin_module_names
    
    while keep_running:
        # Process events first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False
                end_game_type = "quit"
                return end_game_type

        # collect thermal image and display
        if image_buffer_lock.acquire(timeout=0.001):
            if image_buffer is not None:
                # Convert opencv image to pygame compatible image
                #print('found image in buffer')
                recvsurface = pygame.image.frombuffer(image_buffer, IMAGE_SIZE[::-1], 'BGR')
                main_display.blit(recvsurface, IMAGE_DISPLAY_LOCATION)
            image_buffer_lock.release()

        # collect visual image and display
        vis_image = pygame.transform.rotate(vis_cam.get_image(),90)
        original_image = (1920,1080)
        crop_vis_image = vis_image.subsurface(pygame.Rect(600,0,200,1000))
        alpha_val = 128 #50% transparency
        vis_image.set_alpha(alpha_val)
        main_display.blit(vis_image, [10,0])

        # check for UI updates from joystick process
        
        '''
        with open("config.json",'r') as configFile:
            config = json.load(configFile)
            configFile.close()

        if config['space_mode_flag']:
            mode_number = 0
        else:
            mode_number = 1
        if config['image_to_be_captured']:
            photos_left -= 1
            with open('config.json','w') as configFile:
                json.dump(config,configFile)
                configFile.close()
        '''
        try: 
            line = q.get_nowait()
            line = list(str(line))
   
            line = [int(line[3]),int(line[6]),int(line[9])]

        except Exception as e:
            #print('errors in communicating with joy stick programme')
            #print(e)
            line= [0,0,0]
        #print(f' RECIEVED LINE: {line}')
        
        mode_number = line[0]
        if line[1] == 1:
            if previous_line_element_2 == 0:
                photos_left = photos_left - 1
                previous_line_element_2 = 1
        else:
            if previous_line_element_2 == 1:
                photos_left = photos_left - 1
                previous_line_element_2 = 0
        if photos_left == 0:
            end_game_type = "photos_fail"
            return end_game_type

        make_UI(mode_number)
        
        total_time_passed += time.time() - last_time
        last_time = time.time()
        if total_time_passed >= 1:
            countdown_counter -= 1
            total_time_passed = 0
            if countdown_counter <= 0:
                # kill joystick control when out of time
                #os.killpg(os.getpgid(joystick_process.pid), signal.SIGTERM)
                countdown_counter = 0
                end_game_type = "time_fail"
                make_UI(mode_number)
                return end_game_type
                #show_time_up = not show_time_up
                
        #if show_time_up == True:
            #draw_rect(LIGHT_GREY, 250, 450, 500, 100, 20)
            #make_text(40, "Times up!", FONT_COLOR_WHITE, 260, 460)
            #make_text(40, "Thanks for playing :)", FONT_COLOR_WHITE, 260, 505)
        
        
        if countdown_counter <= 10:
            #low time warning
            make_text(25, "LOW POWER", FONT_COLOR_RED, 760, 940)
        # Update display
        pygame.display.flip()
        # print(x, "\t", y)
        
        

    print("Exiting control loop")
    quit_lock.acquire()
    quit_flag = True
    quit_lock.release()


try:
    # begin main loop at kill joystick porcess on keyboard interupt
    if __name__ == '__main__':
        # starting camera service
        '''
        thermal_camera_process = subprocess.Popen('sudo modprobe v4l2loopback;sudo thermapp' ,
                                            shell = True,
                                            stdin = None,
                                            stdout = None,
                                            stderr = subprocess.STDOUT,
                                            bufsize= 1,
                                            preexec_fn =os.setsid)
        '''

        peltier_process = subprocess.Popen('python3 peltier_control.py' ,
                                            shell = True,
                                            stdin = None,
                                            stdout = None,
                                            stderr = subprocess.STDOUT,
                                            bufsize= 1,
                                            preexec_fn =os.setsid)

        argument_parser = argparse.ArgumentParser()
        argument_parser.add_argument("countdown_max", type=int)
        args = argument_parser.parse_args()
        COUNTDOWN_TIME = args.countdown_max
        print("Counting down from: " + str(COUNTDOWN_TIME))


        cam = cv2.VideoCapture('/dev/video2')
        pygame.init()
        pygame.camera.init()
        pygame.joystick.init()
        #print("visual camera count: " + str(pygame.camera.get_count()))
        print("Joystick count: " + str(pygame.joystick.get_count()))
        main_display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # setup thermal camera image reader
        image_reader = ImageReader(cam)
        image_reader.start()

        # start visual camera streaming
        vis_cam = pygame.camera.Camera("/dev/video0",(1920,1080))
        vis_cam.start()

        #start process for joy stick
        joystick_process = subprocess.Popen('python3 joystick.py' ,
                                            shell = True,
                                            stdin = None,
                                            stdout = subprocess.PIPE,
                                            stderr = subprocess.STDOUT,
                                            bufsize= 1,
                                            preexec_fn =os.setsid)
        
        q = queue.LifoQueue()
        t = threading.Thread(target=enqueue_output,args=(joystick_process.stdout,q))
        t.daemon = True
        t.start()
    while restart == True:
    
            end_game_type = main_loop(q)
            restart = end_of_game(end_game_type)

except KeyboardInterrupt:
    print('interrupted with keyboard')
    # clean up even when cancelled
    clean_up_actions()
image_reader.join()        
# clean up at end of game   
clean_up_actions()
