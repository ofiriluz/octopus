import abc
import uuid

class BaseAccessController:
    def __init__(self):
        self.__controller_uuid = uuid.uuid4()

    def get_controller_uuid(self):
        return self.__controller_uuid

    @abc.abstractmethod
    def start_controller(self):
        pass

    @abc.abstractmethod
    def stop_controller(self):
        pass

    @abc.abstractmethod
    def cleanup_resources(self):
        pass

    @abc.abstractmethod
    def is_controller_running(self):
        pass
    
    @abc.abstractmethod
    def get_underlying_engine(self):
        pass
