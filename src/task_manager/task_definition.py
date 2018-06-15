class TaskDefinition:
    def __init__(self, task_definition_id, task_execution_script, task_extra_params, task_output_pipe):
        self.__task_definition_id = task_definition_id
        self.__task_execution_script = task_execution_script
        self.__task_extra_params = task_extra_params
        self.__task_output_pipe = self.__parse_output_pipe(task_output_pipe)
        if not self.__task_output_pipe:
            raise Exception('Invalid task pipe')

    def __parse_output_pipe(self, input_pipe):
        # Output pipe is defined as TYPE[PARAMS_COMMA_SEPERATED]
        # Split by '['
        pipe_info = input_pipe.split('[')
        if len(pipe_info) > 1:
            pipe_type = pipe_info[0]
            # Cleanup the other bracket
            cleanup_bracket_index = pipe_info[1].rfind(']')
            pipe_params = (pipe_info[:cleanup_bracket_index] + pipe_info[cleanup_bracket_index+1:]).split(',')
            return {
                'pipe': pipe_type,
                'params': pipe_params
            }
        return None

    def get_task_definition_id(self):
        return self.__task_definition_id

    def get_task_execution_script(self):
        return self.__task_execution_script

    def get_task_extra_params_dict(self):
        return self.__task_extra_params

    def get_output_pipe(self):
        return self.__task_output_pipe