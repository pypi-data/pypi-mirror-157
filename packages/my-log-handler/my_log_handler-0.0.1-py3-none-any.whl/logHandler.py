import logging
import sys
import os


class Logger:
    def __init__(self, log_path: str) -> None:
        self.log_path = log_path
        if not os.path.isdir(f'{self.log_path}/log'):
            os.mkdir(f'{self.log_path}/log')

        if not os.path.isfile(f'{self.log_path}/id.txt'):
            with open(f'{self.log_path}/id.txt', 'w') as ids:
                ids.write('1')
                self.id = 1
        else:
            with open(f'{self.log_path}/id.txt', 'r') as ids:
                self.id = int(ids.read())

        if self.id > 10:
            with open(f'{self.log_path}/id.txt', 'w') as ids:
                ids.write(str(1))
        else:
            with open(f'{self.log_path}/id.txt', 'w') as ids:
                ids.write(str(self.id+1))

        self.infoLogger()

    def infoLogger(self) -> None:

        _log = logging.getLogger('infoLogger')
        _log.setLevel(logging.INFO)

        _format = '%(asctime)s [%(filename)s : %(funcName)s()] ' + \
            '%(levelname)s: %(message)s'
        _datefmt = '%m/%d/%Y %I:%M:%S %p'
        _filepath = f'{self.log_path}/log/log_{self.id}_INFO.log'

        formatter = logging.Formatter(_format, datefmt=_datefmt)

        fileHandler = logging.FileHandler(_filepath, mode='w')
        fileHandler.setFormatter(formatter)
        _log.addHandler(fileHandler)

        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)
        _log.addHandler(streamHandler)
