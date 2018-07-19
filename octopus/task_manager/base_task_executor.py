import abc

class BaseTaskExecutor:
    def __init__(self, task, task_definition, logger):
        self.__task = task
        self.__task_definition = task_definition
        self.__logger = logger

    def get_task_definition(self):
        return self.__task_definition

    def get_task_executor_logger(self):
        return self.__logger

    def get_task(self):
        return self.__task

    @abc.abstractmethod
    def start_execution(self):
        pass

    @abc.abstractmethod
    def stop_execution(self):
        pass

    @abc.abstractmethod
    def is_running(self):
        pass

    @abc.abstractmethod
    def is_ready_to_execute(self):
        pass

    @abc.abstractmethod
    def get_task_result(self):
        pass

    @abc.abstractmethod
    def get_task_duration(self):
        pass
        