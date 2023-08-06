from logHandler import Logger
import os
import shutil
import logging


class TestLogHandler:
    def setup_class(self):
        self.log_folder = '.temp/log'
        if os.path.isdir(self.log_folder):
            shutil.rmtree(self.log_folder)
        os.makedirs(self.log_folder)

    def teardown_class(self):
        pass

    def test_id(self):
        Logger(self.log_folder)
        assert os.path.isfile(f'{self.log_folder}/id.txt')

    def test_info(self):
        log = logging.getLogger('infoLogger')

        message = "Hello World"
        log.info(message)

        with open(f'{self.log_folder}/id.txt', 'r') as ids:
            self.id = int(ids.read()) - 1

        with open(f'{self.log_folder}/log/log_{self.id}_INFO.log', 'r') as f:
            file = f.read()

        assert message == file.split('INFO: ')[1].split('\n')[0].strip()
