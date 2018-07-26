from threading import Thread, Event, Lock
from octopus.task_manager.base_task_executor import BaseTaskExecutor
from .task_thread_runner import TaskThreadRunner
import datetime
import traceback

class TaskThreadExecutor(BaseTaskExecutor):
    def __init__(self, task, task_definition, logger):
        super().__init__(task, task_definition, logger)
        self.__task_execution_thread = None
        self.__task_execution_mutex = Lock()
        self.__is_running = False
        self.__task_result = None
        self.__task_start_time = None
        self.__task_end_time = None
        self.__task_runner = None

    def __execution_thread(self):
        self.get_task_executor_logger().debug('Execution thread started for task ' + self.get_task()['task_id'])

        try:
            # Get the given task runner object
            self.__task_runner = self.get_task()['task_params']['task_runner']
            if self.__task_runner and issubclass(type(self.__task_runner), TaskThreadRunner):
                # Lock until the process gets into wait state to avoid collision with stop the execution
                self.__task_execution_mutex.acquire()

                self.get_task_executor_logger().debug('Executing task thread {}'.format(self.get_task()['task_id']))
                # Save the task start time
                self.__task_start_time = datetime.datetime.now()

                # Run the task
                self.__task_result = self.__task_runner.run(self.get_task_executor_logger(), **self.get_task()['task_params']['task_runner_params'])

                # Unlock the mutex
                self.__task_execution_mutex.release()

                # Save the task end time
                self.__task_end_time = datetime.datetime.now()
                
                # Callback with the result of the process
                if self.get_task()['task_callback'] and callable(self.get_task()['task_callback']): 
                    self.get_task()['task_callback'](self.get_task()['task_id'], self.__task_result)
            else:
                self.__task_start_time = self.__task_end_time = datetime.datetime.now()
                self.__task_result = 'Error: Invalid task runner'
        except:
            traceback.print_exc()
            self.__task_start_time = self.__task_end_time = datetime.datetime.now()
            self.__task_result = 'Error: Runner exception'
        finally:
            self.__is_running = False

    def start_execution(self):
        if self.__is_running:
            return False

        self.__is_running = True

        # Create and run the execution thread
        self.__task_execution_thread = Thread(target=self.__execution_thread)
        self.__task_execution_thread.start()

    def stop_execution(self):
        if not self.__is_running:
            return False

        self.__is_running = False

        # Stop the execution and wait
        if self.__task_runner:
            self.__task_runner.stop()
        self.__task_execution_thread.join()

    def is_running(self):
        return self.__is_running

    def is_ready_to_execute(self):
        return self.get_task_definition() is not None and self.get_task() is not None and not self.__is_running

    def get_task_result(self):
        return self.__task_result

    def get_task_duration(self):
        return self.__task_end_time - self.__task_start_time