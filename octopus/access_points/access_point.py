import abc

class AccessPoint:
    def __init__(self):
        pass

    @abc.abstractmethod
    def resolve_query(self, logger, query, controllers):
        pass