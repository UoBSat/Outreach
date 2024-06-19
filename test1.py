import time
import RPi.GPIO as GPIO
import numpy as np


dirPin = 2
stepPin = 13
stepsPerRev = 400

 
    
class Stepper():
    def __init__(self,PWM_pin,dir_pin,stepsPerRev = 400):
        self.pins = [PWM_pin,dir_pin]
        self.PWM_pin = PWM_pin
        self.dir_pin = dir_pin
        self.stepsPerRev = stepsPerRev
        GPIO.setmode(GPIO.BCM) # choose the pin numbering
        GPIO.setwarnings(False)
        for pin in self.pins:
            GPIO.setup(pin,GPIO.OUT)
            
        
    def clockwise_inf(self,speed):
        GPIO.output(self.dir_pin,1)
        if (speed < 130) or(speed>2263):
            raise Exception("Speed is not in range 130 to 2263")
        self.PWM = GPIO.PWM(self.PWM_pin,speed)
        self.PWM.start(50)
        
        
    def anticlockwise_inf(self,speed):
        GPIO.output(self.dir_pin,0)
        if (speed < 130) or(speed>2263):
            raise Exception("Speed is not in range 130 to 2263")
        
        self.PWM.start(50)
        
    def stop(self):
        for pin in self.pins:
            GPIO.output(pin,0)
        try:
            self.PWM.stop()
        except:
            None
    def exact_clockwise(self,degrees,speed):
        steps = (degrees/360)*self.stepsPerRev/2
        
        freq = 1/speed
        
        
        
        for i in range(0,int(steps)):
            GPIO.output(self.PWM_pin,1)
            time.sleep(freq/2)
            GPIO.output(self.PWM_pin,0)
            time.sleep(freq/2)
        
        



stepper = Stepper(13,2)

stepper.clockwise_inf(1000)

print("clockwise")

time.sleep(1)


stepper.stop()
time.sleep(0.5)
            
print("anti")


stepper.anticlockwise_inf(1000)     

time.sleep(1)






# for i in range(0,4):
    

#     stepper.exact_clockwise(360, 1000)
#     time.sleep(1)





