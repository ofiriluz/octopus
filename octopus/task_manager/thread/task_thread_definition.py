from octopus.task_manager.base_task_definition import BaseTaskDefinition

TASK_DEFINITION_KEYS = ['task_thread_runner_id']

class TaskThreadDefinition(BaseTaskDefinition):
    def __init__(self, task_definition_id):
        super().__init__(task_definition_id, 'Thread')
        self.__task_thread_runner_id = None

    def init_task_definition(self, task_definition_params):
        # Assert al l params in the params dict
        if all(item in task_definition_params.keys() for item in TASK_DEFINITION_KEYS):
            # Save the args
            self.__task_thread_runner_id = task_definition_params['task_thread_runner_id']

    def get_task_runner_id(self):
        return self.__task_thread_runner_id