import argparse
import copy
import socket
import threading
import time
import constants
from datetime import datetime

import cv2
import pygame
import pygame.image
from gpiozero import Button

DISPLAY_WIDTH = 1000
DISPLAY_HEIGHT = 1000
IMAGE_DISPLAY_LOCATION = (150, 50)
IMAGE_SIZE = (1000, 750)

FONT_SIZE = 60
FONT_COLOR_GREEN = (0, 150, 0)
FONT_COLOR_RED = (150, 0, 0)
COUNTDOWN_DISPLAY_LOCATION = (100, 900)
COUNTDOWN_TIME = 15

INDEX_X_POS = 0
INDEX_X_NEG = 1
INDEX_Y_POS = 2
INDEX_Y_NEG = 3

LIMIT_SWITCH_PINS = [5, 6, 13, 19]


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
                buff = cv2.rotate(cv2.convertScaleAbs(cv2.resize(img, IMAGE_SIZE), 4, -2),
                                  cv2.ROTATE_90_COUNTERCLOCKWISE)
                image_buffer_lock.acquire()
                image_buffer = copy.copy(buff)
                image_buffer_lock.release()
        print("Exiting image loop")


def main_loop(display, joystick):
    global quit_lock, quit_flag, image_buffer_lock, image_buffer
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command_bytes = bytearray(1)
    keep_running = True
    joystick_conn = False
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
            elif event.type == pygame.JOYDEVICEADDED:
                print("Joystick connected")
                joystick_conn = True
                joystick.init()
            elif event.type == pygame.JOYDEVICEREMOVED:
                print("joystick removed")
                joystick_conn = False

        # Read image from cam
        if joystick_conn:
            x = joystick.get_axis(0)
            y = joystick.get_axis(1)
            button = joystick.get_button(0)
        else:
            x = 0.0
            y = 0.0
            button = 0
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

        counter_text = text_font.render(str(countdown_counter), True,
                                        (FONT_COLOR_GREEN if countdown_counter > 10 else FONT_COLOR_RED))
        # Draw rectangle over old text to prevent overlap
        pygame.draw.rect(display, (0, 0, 0),
                         (COUNTDOWN_DISPLAY_LOCATION[0], COUNTDOWN_DISPLAY_LOCATION[1], 100, 60)
                         )
        display.blit(counter_text, COUNTDOWN_DISPLAY_LOCATION)
        # Update display
        pygame.display.flip()

        # Only step steppers beyond a threshold
        if x > 0.5 and not limit_switches[INDEX_X_POS].limit_triggered:
            # print("Stepper in positive x")
            command_bytes[0] |= constants.X_POSITIVE
        elif x < -0.5 and not limit_switches[INDEX_X_NEG].limit_triggered:
            # print("Stepper in negative x")
            command_bytes[0] |= constants.X_NEGATIVE

        if y > 0.5 and not limit_switches[INDEX_Y_POS].limit_triggered:
            # print("Stepper in positive y")
            command_bytes[0] |= constants.Y_POSITIVE
        elif y < -0.5 and not limit_switches[INDEX_Y_NEG].limit_triggered:
            # print("Stepper in negative y")
            command_bytes[0] |= constants.Y_NEGATIVE

        sock.sendto(command_bytes, constants.COMMAND_SERVER)
        command_bytes[0] = 0

        if button:
            image_buffer_lock.acquire()
            if image_buffer is not None and not image_saved:
                count += 1
                new_img_name = str(datetime.now().strftime("%H-%M-%S.jpg"))
                cv2.imwrite("./images/image_" + new_img_name, image_buffer)
                image_saved = True
                # joystick.rumble(0.9, 0.9, 0)
            image_buffer_lock.release()
        else:
            image_saved = False
            # joystick.stop_rumble()

    print("Exiting control loop")
    quit_lock.acquire()
    quit_flag = True
    sock.close()
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
    main_loop(main_display, (pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None))

    image_reader.join()
    pygame.quit()
