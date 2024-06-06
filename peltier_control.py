import RPi.GPIO as GPIO
import time
import random

def main():

    GPIO.setmode(GPIO.BCM)
    peltiers = [26,19,13,6]
    for peltier in peltiers:
        GPIO.setup(peltier, GPIO.OUT)
        GPIO.output(peltier, 0)

    while True:
        # trun random peltier on
        on_pin = random.randrange(0,4)
        GPIO.output(peltiers[on_pin], 1)

        # turn random peltier off
        off_pin = random.randrange(0,4)
        GPIO.output(peltiers[off_pin], 0)

        time.sleep(10)
        
if __name__ == "__main__":
    main()