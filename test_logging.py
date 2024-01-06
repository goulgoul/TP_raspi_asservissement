from threading import RLock
import sqlite3

class Logger:
    _instances = {}
    _lock: RLock = RLock()

    def __new__(cls, name):
        with cls._lock:
            if not name in cls._instances:
                cls._instances[name] = super().__new__(cls)
        return cls._instances[name]

    def __init__(self, name: str = "root_logger"):
       self._name = name
       self._db = sqlite3.connect(f'{name}.db')
       print(self._db.total_changes)

test = Logger('test')
bite = Logger('bite')
retest = Logger('test')
print(test, bite, retest)
