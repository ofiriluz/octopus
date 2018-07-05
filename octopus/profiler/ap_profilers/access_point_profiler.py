import abc

class AccessPointProfiler:
    def __init__(self):
        pass

    @abc.abstractmethod
    def do_profiling(self):
        pass
