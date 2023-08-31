from gpiozero import Button
from signal import pause

switch = Button(5)

switch.when_pressed = lambda: print('P')

pause()
