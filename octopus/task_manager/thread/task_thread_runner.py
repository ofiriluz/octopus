import abc

class TaskThreadRunner:
    def __init__(self):
        pass
        
    @abc.abstractmethod
    def run(self, logger, **kwargs):
        pass

    @abc.abstractmethod
    def stop(self):
        pass