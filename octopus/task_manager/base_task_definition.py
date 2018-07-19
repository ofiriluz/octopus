import abc

class BaseTaskDefinition:
    def __init__(self, task_definition_id, task_definition_type):
        self.__task_definition_id = task_definition_id
        self.__task_definition_type = task_definition_type

    @abc.abstractmethod
    def init_task_definition(self, task_defintion_params):
        pass

    def get_task_definition_id(self):
        return self.__task_definition_id

    def get_task_definition_type(self):
        return self.__task_definition_type