from threading import Thread
import os
import subprocess

class TaskExecutor:
    def __init__(self, task, task_definition):
        self.__task = task
        self.__task_definition = task_definition
        self.__task_execution_thread = None
        self.__is_running = False

    def __execution_thread(self):
        # Assert that the execution script exists
        task_execution_script = self.__task_definition.get_task_execution_script()

        if os.path.exists(task_execution_script):
            # Run the script on a sub process
            script_params = self.__task['task_execution_params']

            


    def start_execution(self):
        if self.__is_running:
            return False

        # Create and run the execution thread
        self.__task_execution_thread = Thread(self.__execution_thread)
        self.__task_execution_thread.start()

    def stop_execution(self):
        if not self.__is_running:
            return False

        # Stop the execution and wait
        # TODO

    def is_running(self):
        return self.__is_running

    def is_ready_to_execute(self):
        return self.__task_definition is not None and self.__task is not None and not self.__is_running