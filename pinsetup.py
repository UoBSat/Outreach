import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIOs = [4, 3, 2, 18, 20, 16, 12, 7]

for gpio in GPIOs:
    GPIO.setup(gpio, GPIO.OUT)
    GPIO.output(gpio, 0)
    
    
#GPIO.cleanup()