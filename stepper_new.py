import time
import RPi.GPIO as GPIO
import numpy as np




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
        
        self.PWM = GPIO.PWM(self.PWM_pin,1000)
        
        
            
        
    def clockwise_inf(self,speed):
        GPIO.output(self.dir_pin,1)
        if (speed < 130) or(speed>2263):
            raise Exception("Speed is not in range 130 to 2263")
        self.PWM.start(50)
        self.PWM.ChangeFrequency(speed)
        
        
        
    def anticlockwise_inf(self,speed):
        GPIO.output(self.dir_pin,0)
        if (speed < 130) or(speed>2263):
            raise Exception("Speed is not in range 130 to 2263")
        
        self.PWM.start(50)
        self.PWM.ChangeFrequency(speed)
        
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
        
        







