from gpiozero import LED, Button, PWMOutputDevice, RotaryEncoder
from signal import pause
from time import sleep

led = LED(21)	
button = Button(22)
button.when_pressed = led.on
button.when_released = led.off
encoder = RotaryEncoder(17, 27, wrap=False, max_steps = 8)
encoder.steps = -8
fan = PWMOutputDevice(12, frequency = 2)

while(True):
    print(encoder.steps)
    fan.value = (encoder.steps+8)/16
    sleep(0.5)

pause()
