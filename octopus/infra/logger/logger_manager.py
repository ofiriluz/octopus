import datetime
from .logger import Logger, INFO
import os

class LoggerManager:
    def __init__(self, logger_folder_path, is_console_allowed=True):
        self.__loggers = {}
        self.__logger_folder_path = logger_folder_path
        self.__is_console_allowed = is_console_allowed

    def __get_log_path(self, logger_name):
        # Create the full logger path
        return os.path.join(self.__logger_folder_path, 
                            "{}_{}.log".format(
                                datetime.datetime.now().strftime('%Y_%m_%d-%H_%M_%S'), 
                                logger_name))

    def open_logger(self, logger_name, log_level=INFO):
        # Get the logger file path
        log_path = self.__get_log_path(logger_name)

        # Create, save and return the logger
        logger_obj = Logger(logger_name, log_level, log_path, self.__is_console_allowed)
        logger_obj.open_logger()
        self.__loggers[logger_name] = logger_obj

        return logger_obj

    def close_logger(self, logger_name):
        # Check if logger exists, and clean it
        if logger_name in self.__loggers.keys():
            self.__loggers[logger_name].close_logger()
            del self.__loggers[logger_name]
            return True
        return False

    def close_all_loggers(self):
        # Go over every logger and close it
        for logger_name in list(self.__loggers):
            self.close_logger(logger_name)
