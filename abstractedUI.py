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

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 1000
IMAGE_DISPLAY_LOCATION = (150, 50)
IMAGE_SIZE = (1000, 750)

FONT_SIZE = 60
FONT_COLOR_GREEN = (0, 150, 0)
FONT_COLOR_RED = (150, 0, 0)
COUNTDOWN_DISPLAY_LOCATION = (100, 900)
COUNTDOWN_TIME = 15

LIMIT_SWITCH_PINS = [6,5,19,13]

global image_buffer, image_buffer_lock, quit_lock, image_available, quit_flag
image_buffer = None
image_buffer_lock = threading.Lock()
quit_lock = threading.Lock()
image_available = False
quit_flag = False



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
                buff = cv2.rotate(cv2.convertScaleAbs(cv2.resize(img, IMAGE_SIZE), 4, -2), cv2.ROTATE_90_COUNTERCLOCKWISE)
                image_buffer_lock.acquire()
                image_buffer = copy.copy(buff)
                image_buffer_lock.release()
        print("Exiting image loop")


def main_loop(display):
    global quit_lock, quit_flag, image_buffer_lock, image_buffer
    keep_running = True
    clock = pygame.time.Clock()
    count = 0
    image_saved = True
    last_time = time.time()
    total_time_passed = 0
    countdown_counter = COUNTDOWN_TIME
    text_font = pygame.font.Font("freesansbold.ttf", FONT_SIZE)
    while keep_running:
        # Process events first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keep_running = False
            

        if image_buffer_lock.acquire(timeout=0.001):
            if image_buffer is not None:
                # Convert opencv image to pygame compatible image
                display.blit(pygame.image.frombuffer(image_buffer, IMAGE_SIZE[::-1], 'BGR'), IMAGE_DISPLAY_LOCATION)
            image_buffer_lock.release()
        
        total_time_passed += time.time() - last_time
        last_time = time.time()
        if total_time_passed >= 1:
            countdown_counter -= 1
            total_time_passed = 0
            if countdown_counter <= 0:
                countdown_counter = 0

        counter_text = text_font.render(str(countdown_counter), True, (FONT_COLOR_GREEN if countdown_counter > 10 else FONT_COLOR_RED))
        # Draw rectangle over old text to prevent overlap
        pygame.draw.rect(display, (0, 0, 0), 
                (COUNTDOWN_DISPLAY_LOCATION[0], COUNTDOWN_DISPLAY_LOCATION[1], 100, 60)
                )
        display.blit(counter_text, COUNTDOWN_DISPLAY_LOCATION)
        # Update display
        pygame.display.flip()
        # print(x, "\t", y)
        
        

    print("Exiting control loop")
    quit_lock.acquire()
    quit_flag = True
    quit_lock.release()

if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("countdown_max", type=int)
    args = argument_parser.parse_args()
    COUNTDOWN_TIME = args.countdown_max
    print("Counting down from: " + str(COUNTDOWN_TIME))


    cam = cv2.VideoCapture(0)
    pygame.init()
    pygame.joystick.init()
    print("Joystick count: " + str(pygame.joystick.get_count()))
    main_display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    image_reader = ImageReader(cam)
    image_reader.start()
    main_loop(main_display)

    image_reader.join()
    pygame.quit()
