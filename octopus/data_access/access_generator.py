import abc

class BaseAccessGenerator:
    def __init__(self):
        pass

    @abc.abstractmethod
    def generate_access_controller(self, **kwargs):
        pass