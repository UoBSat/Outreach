from stepper import Stepper
import time




dirPin_x = 2
stepPin_x = 13
    
dirPin_y = 3
stepPin_y = 12
    
x_stepper = Stepper(stepPin_x,dirPin_x)
    
y_stepper = Stepper(stepPin_y,dirPin_y)



x_stepper.clockwise_inf(500)

time.sleep(2)
x_stepper.stop()


x_stepper.anticlockwise_inf(500)


time.sleep(2)
x_stepper.stop()