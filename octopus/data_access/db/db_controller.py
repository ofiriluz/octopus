import abc
import uuid

class BaseDBController:
    def __init__(self, connection_info):
        self.__connection_host = connection_info[0]
        self.__connection_port = connection_info[1]
        self.__controller_uuid = uuid.uuid4()

    def get_controller_uuid(self):
        return self.__controller_uuid

    def get_controller_host(self):
        return self.__connection_host

    def get_controller_port(self):
        return self.__connection_port

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