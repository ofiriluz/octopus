import abc

class Profiler:
    def __init__(self):
        pass

    @abc.abstractmethod
    def do_profiling(self, logger, query, controllers):
        pass
