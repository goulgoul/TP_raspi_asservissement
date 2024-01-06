from threading import Timer, RLock
from gpiozero import CPUTemperature, PWMOutputDevice, Button, RotaryEncoder, LED
from time import sleep
import sqlite3
from weakref import WeakValueDictionary
import json
from os import path, mkdir

VERSION = "1.6-07-01-2024"

MEASUREMENT_PERIOD_SECONDS = 5  # Sample the CPU temperature every 5 seconds
DB_FLUSH_PERIOD_SECONDS = 3600 # Delete old entries in the database every hour 
FAN_PWM_PIN = 12                # Pin used for PWM (GPIO12 by default)
PWM_FREQUENCY = 1               # PWM signal frequency (1 Hz by default)
BUTTON_PIN = 22                 # GPIO linked to the push button of the encoder (GPIO22 by default
DT_PIN = 27                     # Pin used for the DT encoder signal
CLK_PIN = 17                    # Pin used for the encoder clock signal
LED_PIN = 8                     # Pin used for the LED indicator (GPIO08 by default) 
ENCODER_MAX_STEPS = 8
DEFAULT_TARGET_TEMPERATURE = 40
KP = 2.0
AUTOSTART = True
DB_DIRECTORY = '/cputemp/db'
                           
class Logger:
    _instances = WeakValueDictionary()
    _lock: RLock = RLock()
    def __new__(cls, db_name: str = 'default.db'):
        with cls._lock:
            if db_name not in cls._instances:
                instance = super(Logger, cls).__new__(cls)
                cls._instances[db_name] = instance
        return cls._instances[db_name]

    def __init__(self, db_name: str = 'default.db'):
        if not path.isdir(DB_DIRECTORY):
            mkdir(DB_DIRECTORY)
        self._db = sqlite3.connect(f'{DB_DIRECTORY}/{db_name}', check_same_thread=False)
        self._cursor = self._db.cursor()
        self._cursor.execute('CREATE TABLE IF NOT EXISTS Traces (datetime_text, record)')
        self._db_name = db_name
        self._timer = None

    def log(self, message: str = 'empty_record') -> None:
        self._cursor.execute(f"INSERT INTO Traces (datetime_text, record) VALUES (DATETIME('now'), '{message}')")
        self._db.commit()
        self.clean_db()

    def clean_db(self) -> None:
        outdated_entries = self._cursor.execute("SELECT * FROM Traces WHERE datetime_text < DATETIME('now', '-7 second')").fetchall()
        print(outdated_entries)
        if outdated_entries == []: 
            return
        self._cursor.execute("DELETE FROM Traces WHERE datetime_text < DATETIME('now', '-7 second')")
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
        # self._target_temperature = self.get_temperature()
        self._target_temperature = DEFAULT_TARGET_TEMPERATURE 
        self._encoder_position = self._encoder.steps 

        self._logger = Logger('cputemp.db')

        self.start()


    def start(self) -> None:
        self._timer = Timer(MEASUREMENT_PERIOD_SECONDS, function=self.on_timeout)
        self._timer.start()

    def stop(self) -> None:
        self._timer.cancel()
        del self._logger

    def on_timeout(self) -> None:
        self.start()
        self.regulate_temperature()
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
                'error': round(temp - self._target_temperature, 1),
                'output': self._fan_rate
                }
        self._logger.log(f'{__class__.__name__}: regulate_temperature() {json.dumps(json_record)}')
        return

    def set_target_temperature(self) -> None:
        self._target_temperature += (self._encoder.steps - self._encoder_position)
        self._encoder_position = self._encoder.steps
        print(f'target temp {self._target_temperature}')
        self.regulate_temperature()

    
    def toggle(self) -> None:
        self._enabled = not self._enabled
        self._led.value = self._enabled
        #print(f'Temperautre regulator state: {self._enabled}')
        self.regulate_temperature()



def main_thread():
    main_logger = Logger('cputemp.db')
    try:
        fan = FanControl()
        while(True):
            sleep(5)
            # print(dict(Logger._instances))
    except KeyboardInterrupt:
        # print('\nExiting program after KeyboardInterrupt was raised')
        fan.stop()
    

if __name__ == '__main__':
    main_thread()
