from threading import Timer, RLock
from gpiozero import CPUTemperature, PWMOutputDevice, Button, RotaryEncoder, LED
from time import sleep
import sqlite3
import json
from os import path, mkdir

VERSION = "1.5-06-01-2024"

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
                           
class Logger():
    _instances = {}
    _lock: RLock = RLock()
    def __new__(cls, name: str = 'root_logger', log_file_path: str = './root_logger.db'):
        with cls._lock:
            if not name in cls._instances:
                cls._instances[name] = super().__new__(cls)
        return cls._instances[name]

    def __init__(self, name: str = 'root_loger', log_file_path: str = './root_logger.db'):
        self._name = name
        log_dir = log_file_path.rsplit('/', 1)[0]
        if not path.isdir(log_dir):
            mkdir(log_dir)
        self._db = sqlite3.connect(log_file_path, check_same_thread=False)
        self._cursor = self._db.cursor()
        self._cursor.execute(f'CREATE TABLE IF NOT EXISTS {self._name} (datetime_text, record)')

    def log(self, message: str = 'empty_record') -> None:
        self._cursor.execute(f"INSERT INTO {self._name} (datetime_text, record) VALUES (DATETIME('now'), '{message}')")

        self._db.commit()

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

        self._logger = Logger(name='cputemp_logger', log_file_path='/cputemp/db/cputemp.db')

        self.start()


    def start(self) -> None:
        self._timer = Timer(MEASUREMENT_PERIOD_SECONDS, function=self.on_timeout)
        self._timer.start()

    def stop(self) -> None:
        self._timer.cancel()

    def on_timeout(self) -> None:
        self.start()
        fan.regulate_temperature()
        # print(f'current CPU temparature: {self.get_temperature()} °C')

    @staticmethod
    def get_temperature() -> float:
        return round(CPUTemperature().temperature, 1)
        
    def regulate_temperature(self) -> None:
        if self._enabled:    
            temp = self.get_temperature()
            self._fan_rate = round(KP * (temp - self._target_temperature)/self._target_temperature, 1)
            self._fan.value = self._fan_rate if self._fan_rate >= 0 else 0
        else:
            temp = 0
            self._fan_rate = self._fan.value = 0

        json_record = {
                'enabled': json.dumps(self._enabled),
                'temp': temp,
                'setpoint': self._target_temperature,
                'error': temp - self._target_temperature,
                'output': self._fan_rate
                }
        self._logger.log(json.dumps(json_record))
        return

    def set_target_temperature(self) -> None:
        self._target_temperature += (self._encoder.steps - self._encoder_position)
        self._encoder_position = self._encoder.steps
        #print(f'target temp {self._target_temperature}')
        self.regulate_temperature()

    
    def toggle(self) -> None:
        self._enabled = not self._enabled
        self._led.value = self._enabled
        #print(f'Temperautre regulator state: {self._enabled}')
        self.regulate_temperature()



if __name__ == '__main__':
    try:
        fan = FanControl()
        print(f'active loggers: {Logger._instances}')
        while(True):
            sleep(5)
    except KeyboardInterrupt:
        print('\nExiting program after KeyboardInterrupt was raised')
        fan.stop()
