import RPi.GPIO as GPIO
import time


step_sequence = [
        [0, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 1, 0, 1],
        [0, 0, 0, 1],
       [1, 0, 0, 1],
       [1, 0, 0, 0],
       [1, 0, 1, 0],
       [0, 0, 1, 0],
       [0, 1, 1, 0],
        [0, 0, 0, 0]
        ]

#step_sequence = [
#        [1, 0, 0, 1],
#        [1, 1, 0, 0],
#        [0, 1, 1, 0],
#        [0, 0, 1, 1],
#        [0, 0, 0, 0]
#        ]

step_delay = 0.0009


class Stepper:
    def __init__(self, channel_A_1, channel_A_2, channel_B_1, channel_B_2):
        self.pins = [channel_A_1, channel_A_2, channel_B_1, channel_B_2]
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
        self.write([0, 0, 0, 0])

    def write(self, pin_outputs):
        for i in range(len(self.pins)):
            GPIO.output(self.pins[i], pin_outputs[i])

    def step_clockwise(self):
        for step_params in step_sequence:
            self.write(step_params)
            time.sleep(step_delay)

    def step_counterclockwise(self):
        for step_params in step_sequence[::-1]:
            self.write(step_params)
            time.sleep(step_delay)
    