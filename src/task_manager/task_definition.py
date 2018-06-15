import re

# Supported types to convertors
SUPPORTED_TYPES = {'int': int, 'string': str, 'bool': bool}

class TaskDefinition:
    def __init__(self, task_definition_id, task_execution_script, task_shell_executor, task_extra_params, task_output_pipe):
        self.__task_definition_id = task_definition_id
        self.__task_execution_script = task_execution_script
        self.__task_shell_executor = task_shell_executor
        self.__task_extra_params = task_extra_params
        self.__task_output_pipe = self.__parse_output_pipe(task_output_pipe)
        if not self.__task_output_pipe:
            raise Exception('Invalid task pipe')
    def __validate_type(self, value, param_type):
        # Supported types are string, int, bool
        # If doesnt exist, ignore
        if not param_type in SUPPORTED_TYPES.keys():
            return False
        try:
            # Try and parse 
            SUPPORTED_TYPES[param_type](value)
        except:
            return False
        return True

    def __clean_extra_params(self, extra_params):
        cleaned_extra_params = {}
        for extra_param in extra_params.keys():
            # Find if the param is in the allowed extra params list
            for allowd_param in self.__task_extra_params:
                # Also validate type
                if allowd_param['name'] == extra_param and self.__validate_type(extra_params[extra_param], allowd_param['type']):
                    cleaned_extra_params[extra_param] = extra_params[extra_param]
        return cleaned_extra_params

    def __create_output_pipe(self, task_output_pipe, extra_params):
        # Go over the params dict and replace any mustached params with the given extra params
        for pipe_key in task_output_pipe['params'].keys():
            pipe_value = task_output_pipe['params'][pipe_key]
            if self.__mustached(pipe_value):
                # Remove the mustache
                none_mustached_pipe_param = self.__remove_mustache(pipe_value)
                # Find and replace the fitting parameter
                for extra_param in extra_params.keys():
                    if extra_param == none_mustached_pipe_param:
                        pipe_value = extra_params[extra_param]
                        break
            # Save the param to the dict
            task_output_pipe['params'][pipe_key] = pipe_value
        return task_output_pipe

    def __mustached(self, value):
        # Check if starts and ends with double brackets
        return value.startswith('{{') and value.endswith('}}')

    def __remove_mustache(self, value):
        # Remove double brackets from start and end
        return re.sub('(^{{) | (}}$)', '', value)

    def __parse_output_pipe(self, input_pipe):
        # Output pipe is defined as TYPE[PARAMS_COMMA_SEPERATED]
        # Split by '['
        pipe_info = input_pipe.split('[')
        if len(pipe_info) > 1:
            pipe_type = pipe_info[0]
            # Cleanup the other bracket
            cleanup_bracket_index = pipe_info[1].rfind(']')
            pipe_params = (pipe_info[:cleanup_bracket_index] + pipe_info[cleanup_bracket_index+1:])

            # Create the params dict
            params_dict = {}
            for pipe_param in pipe_params.split(';'):
                pipe_param_splitted = pipe_param.split('=')
                # Save the param to the dict
                params_dict[pipe_param_splitted[0]] = pipe_param_splitted[1]
            # Return the final pipe
            return {
                'pipe': pipe_type,
                'params': params_dict
            }
        return None

    def get_task_definition_id(self):
        return self.__task_definition_id

    def get_task_execution_script(self):
        return self.__task_execution_script

    def get_task_shell_executor(self):
        return self.__task_shell_executor

    def get_task_extra_params_dict(self):
        return self.__task_extra_params

    def get_output_pipe(self, extra_params=None):
        task_output_pipe = self.__task_output_pipe
        if extra_params:
            # Clean unallowed params from the given extra params
            extra_params_cleaned = self.__clean_extra_params(extra_params)
            # Create the parsed output pipe
            task_output_pipe = self.__create_output_pipe(task_output_pipe, extra_params_cleaned)
        return self.__task_output_pipe