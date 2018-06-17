from octopus.infra.logger import LoggerManager, DEBUG, INFO
import tempfile
import os
import unittest

class LoggerTests(unittest.TestCase):
    def setUp(self):
        p = os.path.join(tempfile.gettempdir(), 'logtmptests')
        if not os.path.exists(p):
            os.makedirs(p)
        self.logger_manager = LoggerManager(p, False)

    def test_simple_logger_manager(self):
        logger = self.logger_manager.open_logger('TestLogger')
        path = logger.get_log_file_path()
        logger.info('Hello World')
        self.logger_manager.close_logger('TestLogger')
        with open(path, 'r') as f:
            log = '\n'.join(line.strip() for line in f.readlines())
            # Remove datetime
            idx = log.find(']')
            log = log[idx+1:]
            self.assertEqual('[TestLogger][Info]: Hello World', log)

if __name__ == '__main__':
    unittest.main(exit=False)
