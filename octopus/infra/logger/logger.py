import os
import datetime
import sys

DEBUG=0
INFO=1
WARN=2
ERROR=3

LEVEL_TO_STRING_DICT = {
    DEBUG:'Debug',
    INFO:'Info',
    WARN:'Warning',
    ERROR:'Error'
}

class Logger:
    def __init__(self, logger_name, log_level, logger_path=None, output_to_console=True):
        self.__logger_name = logger_name
        self.__log_level = log_level
        self.__logger_path = logger_path
        self.__logger_file = None
        self.__is_logger_opened = False
        self.__output_to_console = output_to_console

    def __write_log(self, msg, type_str):
        # First create the formatted message
        formatted_msg = '[{}][{}][{}]: {}\n'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                  self.__logger_name,
                                                  type_str,
                                                  msg)
        # Check if writeable to console
        if self.__output_to_console:
            sys.stdout.write(formatted_msg)

        # Check if writeable to file
        if self.__logger_file:
            self.__logger_file.write(formatted_msg)
            self.__logger_file.flush()

    def open_logger(self):
        # This is only called from the logger manager
        # Check if logger is already opened
        if self.__is_logger_opened:
            return False

        self.__is_logger_opened = True

        if self.__logger_path:
            # Create the logger directory if it does not exist
            directory = os.path.dirname(self.__logger_path)
            os.makedirs(directory, exist_ok=True)

            # Open the file
            self.__logger_file = open(self.__logger_path, 'w')

        return True

    def close_logger(self):
        # This is only called from the logger manager
        # Check if logger is already opened
        if not self.__is_logger_opened:
            return False

        self.__is_logger_opened = False
        # Close the logger file
        if self.__logger_file:
            self.__logger_file.close()
            self.__logger_file = None

        return True

    def get_log_file_path(self):
        return self.__logger_path

    def debug(self, msg):
        # Only write log by log level
        if self.__log_level <= DEBUG:
            self.__write_log(msg, LEVEL_TO_STRING_DICT[DEBUG])

    def info(self, msg):
        # Only write log by log level
        if self.__log_level <= INFO:
            self.__write_log(msg, LEVEL_TO_STRING_DICT[INFO])

    def warn(self, msg):
        # Only write log by log level
        if self.__log_level <= WARN:
            self.__write_log(msg, LEVEL_TO_STRING_DICT[WARN])

    def error(self, msg):
        # Only write log by log level
        if self.__log_level <= ERROR:
            self.__write_log(msg, LEVEL_TO_STRING_DICT[ERROR])
