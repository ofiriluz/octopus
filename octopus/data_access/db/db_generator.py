import abc

class BaseDBGenerator:
    def __init__(self):
        pass

    @abc.abstractmethod
    def generate_db_controller(self, connection_info, **kwargs):
        pass