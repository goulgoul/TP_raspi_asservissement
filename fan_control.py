from threading import Timer
from gpiozero import CPUTemperature, PWMOutputDevice, Button, RotaryEncoder
from time import sleep


MEASUREMENT_PERIOD_SECONDS = 5
FAN_PWM_PIN = 12
PWM_FREQUENCY = 1
BUTTON_PIN = 22
DT_PIN = 27
CLK_PIN = 17
ENCODER_MAX_STEPS = 8

class FanControl:
    __enabled = True
    def __init__(self) -> None:
        print("fan init")
        self._timer = None
        self._fan = PWMOutputDevice(FAN_PWM_PIN, frequency=PWM_FREQUENCY)
        self._button = Button(BUTTON_PIN)
        self._encoder = RotaryEncoder(CLK_PIN, DT_PIN, wrap = False, max_steps = ENCODER_MAX_STEPS)
        self._fan_rate = 0
        self._encoder.when_rotated = self.update
        self._button.when_pressed = self.toggle
        self._state = 0
        self._target_temperature = self.get_temperature()
        self._encoder_position = self._encoder.steps 


    def start(self) -> None:
        self._timer = Timer(MEASUREMENT_PERIOD_SECONDS, function=self.on_timeout)
        self._timer.start()

    def on_timeout(self) -> None:
        if not FanControl.__enabled:
            print("OFF")
            return
        self.start()
        print(fan.get_temperature())

    @staticmethod
    def get_temperature() -> float:
        return round(CPUTemperature().temperature, 1)
        
    def update(self) -> None:
        self._error = self._target_temperature - self.get_temperature()
        self._target_temperature += (self._encoder.steps - self._encoder_position)
        
        print(self._target_temperature)
        self._encoder_position = self._encoder.steps
    
    def toggle(self) -> None:
        FanControl.__enabled = not FanControl.__enabled
        if FanControl.__enabled:
            self.start()

fan = FanControl()
fan.start()

while(True):
    sleep(15)
