from gpiozero import Button
from signal import pause

switch = Button(20)

switch.when_pressed = lambda: print('P')

pause()
