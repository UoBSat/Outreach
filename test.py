from stepper import Stepper
import time
import RPi.GPIO as GPIO


def Turn_off(pins):
    for pin in pins:
        GPIO.output(pin,False)


GPIO.setmode(GPIO.BCM) # choose the pin numbering

GPIO.setwarnings(False)



pins = [4,3,2,17,13,12]
# stepper_1 = Stepper(4,3,2,17) 


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
for pin in pins:
    GPIO.setup(pin,GPIO.OUT)
    
Turn_off(pins)
step = 0.0001

# GPIO.output(3,True)

# GPIO.output(2,True)

# pi_pwm = GPIO.PWM(13,1000)
# pi_pwm.start(0)
# pi_pwm.ChangeDutyCycle(50)


# time.sleep(5)
Turn_off(pins)




In_1 = 17
In_2 = 4
In_3 = 3
In_4 = 2
Ena = 13
Enb = 12



#Forward
GPIO.output(In_3,1)
GPIO.output(In_4,0)
GPIO.output(In_1,1)
GPIO.output(In_2,0)


freq = 0.005
duty = 50




for i in range(0,100):
    GPIO.output(Ena,1)
    GPIO.output(Enb,0)
    time.sleep(freq)
    GPIO.output(Ena,1)
    GPIO.output(Enb,1)
    time.sleep(freq/10)
    GPIO.output(Ena,0)
    GPIO.output(Enb,1)
    time.sleep(freq)

time.sleep(2)

Turn_off(pins)












