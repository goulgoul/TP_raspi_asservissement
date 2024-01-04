from threading import Timer
from gpiozero import CPUTemperature, PWMOutputDevice, Button, RotaryEncoder, LED
from time import sleep

VERSION = "1.4-04-01-2024"

MEASUREMENT_PERIOD_SECONDS = 5  # Sample the CPU temperature every X seconds
FAN_PWM_PIN = 12                # Pin used for PWM (GPIO12 by default)
PWM_FREQUENCY = 1               # PWM signal frequency (1 Hz by default)
BUTTON_PIN = 22                 # GPIO linked to the push button of the encoder (GPIO22 by default
DT_PIN = 27                     # Pin used for the DT encoder signal
CLK_PIN = 17                    # Pin used for the encoder clock signal
LED_PIN = 8                     # Pin used for the LED indicator (GPIO08 by default) 
ENCODER_MAX_STEPS = 8
KP = 2.0
AUTOSTART = True






class FanControl:
    def __init__(self) -> None:
        self._timer = None
        self._led = LED(LED_PIN)
        self._fan = PWMOutputDevice(FAN_PWM_PIN, frequency=PWM_FREQUENCY)
        self._button = Button(BUTTON_PIN)
        self._encoder = RotaryEncoder(CLK_PIN, DT_PIN, wrap = False, max_steps = ENCODER_MAX_STEPS)

        self._fan_rate = 0
        self._encoder.when_rotated = self.set_target_temperature
        self._button.when_pressed = self.toggle
        self._enabled = AUTOSTART
        self._led.value = self._enabled
        self._target_temperature = self.get_temperature()
        self._encoder_position = self._encoder.steps 

        self.start()


    def start(self) -> None:
        self._timer = Timer(MEASUREMENT_PERIOD_SECONDS, function=self.on_timeout)
        self._timer.start()

    def stop(self) -> None:
        self._timer.cancel()

    def on_timeout(self) -> None:
        self.start()
        print(f"current CPU temparature: {self.get_temperature()} °C")

    @staticmethod
    def get_temperature() -> float:
        return round(CPUTemperature().temperature, 1)
        
    def regulate_temperature(self) -> None:
        if not self._enabled:
            self._fan_rate = self._fan.value = 0
            return
        self._fan_rate = KP * (self.get_temperature() - self._target_temperature)/self._target_temperature
        self._fan.value = round(self._fan_rate, 1) if self._fan_rate >= 0 else 0
    
    def set_target_temperature(self) -> None:
        self._target_temperature += (self._encoder.steps - self._encoder_position)
        self._encoder_position = self._encoder.steps
        print(f"target temp {self._target_temperature}")
        self.regulate_temperature()

    
    def toggle(self) -> None:
        self._enabled = not self._enabled
        self._led.value = self._enabled
        print(f"Temperautre regulator state: {self._enabled}")
        self.regulate_temperature()




try:
    fan = FanControl()
    while(True):
        sleep(5)
except KeyboardInterrupt:
    print("\nExiting program after KeyboardInterrupt was raised")
    fan.stop()
