from threading import Lock, Event, Thread
from .task_definition import TaskDefinition
from .task_executor import TaskExecutor
from octopus.infra.logger import LoggerManager, Logger, DEBUG, INFO
import time
import json
import tempfile
import uuid
import os

REQUIRED_TASK_DEFINITION_KEYS = ['task_definition_id', 'task_execution_script', 'task_shell_executor', 'task_output_pipe']
OPTIONAL_TASK_DEFINITION_KEYS = ['task_extra_params']
DEFAULT_MAX_RUNNING_TASKS = 5
DEFAULT_POOL_TIMEOUT = 10
DEFAULT_LOG_PATH = os.path.join(tempfile.gettempdir(), 'tmplogs')
DEFAULT_SLEEP_PERIOD = 3
DEFAULT_LOG_LEVEL = INFO

class TaskManager:
    def __init__(self, 
                max_running_tasks=DEFAULT_MAX_RUNNING_TASKS, 
                pool_timeout=DEFAULT_POOL_TIMEOUT,
                log_path=DEFAULT_LOG_PATH,
                log_level=DEFAULT_LOG_LEVEL):
        self.__tasks_queue = []
        self.__task_executors = []
        self.__tasks_mutex = Lock() 
        self.__tasks_pool_event = Event()
        self.__is_task_manager_running = False
        self.__tasks_history = {}
        self.__task_definitions = {}
        self.__max_running_tasks = max_running_tasks
        self.__pool_timeout = pool_timeout
        self.__tasks_thread = None
        self.__cleaner_thread = None
        self.__logger_manager = LoggerManager(log_path)
        self.__logger = self.__logger_manager.open_logger('TaskManager', DEFAULT_LOG_LEVEL)

    def __init_task_manager(self):
        # Reset all the needed and allowed data structures
        self.__task_executors = []
        self.__tasks_history = {}
        # Reset the threads, shouldnt be running here
        self.__tasks_thread = self.__cleaner_thread = None
        # Open the logger if not opened
        if not self.__logger:
            self.__logger = self.__logger_manager.open_logger('TaskManager', DEFAULT_LOG_LEVEL)

    def __execute_task(self, task, task_defintion):
        self.__logger.debug('Preparing to execute task ' + task['task_id'])

        # Create a logger for the executor
        executor_logger = self.__logger_manager.open_logger(task['task_id'], DEFAULT_LOG_LEVEL)

        # Create the task executor
        task_executor = TaskExecutor(task, task_defintion, executor_logger)

        # Check if its ready to be executed
        if task_executor.is_ready_to_execute():
            self.__logger.debug('Starting task execution ' + task['task_id'])
            # Run it, will create a new thread inside
            task_executor.start_execution()

            # Sace the executor
            self.__task_executors.append(task_executor)

            return True
        return False

    def __is_task_pool_full(self):
        return len(self.__task_executors) == self.__max_running_tasks
    
    def __has_more_tasks(self):
        return len(self.__tasks_queue) > 0

    def __has_more_executors_running(self):
        return len(self.__task_executors) > 0

    def __pop_next_task(self):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Check if there is a task to pop
            if len(self.__tasks_queue) > 0:
                # Pop and return the task
                return self.__tasks_queue.pop(0)
        return None

    def __retrieve_task_definition(self, task_definition_id):
        # Return the task defintion if exists
        if task_definition_id in self.__task_definitions.keys():
            return self.__task_definitions[task_definition_id]
        return None

    def __tasks_cleaner_thread(self):
        self.__logger.info('Task cleaner thread started.')
        # Run untill the manager is stopped
        while self.__is_task_manager_running:
            indices_to_remove = []
            # Check if any task is done
            for index, task_executor in enumerate(self.__task_executors):
                if not task_executor.is_running():
                    indices_to_remove.append(index)
                    # Save the task result in the history
                    self.__tasks_history[task_executor.get_task()['task_id']] = {
                        'task_id': task_executor.get_task()['task_id'],
                        'task_result': task_executor.get_task_result(),
                        'task_duration': task_executor.get_task_duration()
                    }

            # Remove the indexes
            with self.__tasks_mutex:
                self.__task_executors = [i for j, i in enumerate(self.__task_executors) if j not in indices_to_remove]
            time.sleep(1)
                    
    def __tasks_runner_thread(self):
        self.__logger.info('Task runner thread started.')
        # Run untill the manager is stopped
        while self.__is_task_manager_running:
            # If the pool is full, wait for a trigger, with timeout incase a task has failed
            if self.__is_task_pool_full():
                self.__tasks_pool_event.wait(timeout=self.__pool_timeout)

            # Check if more tasks exist in the queue
            if self.__has_more_tasks():
                # Get the next task to deploy
                task = self.__pop_next_task()
                if task:
                    # Get the task definition of this task
                    task_def = self.__retrieve_task_definition(task['task_definition_id'])
                    if task_def:
                        self.__logger.debug('Adding task {} to the pool'.format(task['task_id']))
                        # Execute the task
                        self.__execute_task(task, task_def)
            # Sleep to not overrun the task manager
            time.sleep(0.1)
        
        # Close all the executors
        for executor in self.__task_executors:
            executor.stop_execution()

        # Wait for the remaining tasks to end
        while self.__has_more_executors_running():
            time.sleep(0.5)
                
    def add_task(self, task_definition_id, task_execution_params_list, task_extra_params, task_callback=None):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Get the task definition
            task_def = self.__retrieve_task_definition(task_definition_id)
            # Assert that execution params are specificly a list 
            if task_def is not None and type(task_execution_params_list) is list:
                # Create and add the task
                # Generate a task id
                task_id = str(uuid.uuid4())

                self.__logger.info('Adding task with id {}'.format(task_id))
                # Create the task dict
                task = {
                    "task_id": task_id,
                    "task_definition_id": task_definition_id,
                    "task_execution_params": task_execution_params_list,
                    "task_extra_params": task_extra_params,
                    "task_callback": task_callback
                }
                # Save the task 
                self.__tasks_queue.append(task)

                # Return the created task id
                return task_id

        return None

    def stop_executed_task(self, task_id, timeout=None):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Timeout exception 
            try:
                for task_executor in self.__task_executors:
                    # Find the executor
                    if task_executor.get_task()['task_id'] == task_id:
                        self.__logger.info('Stopping task execution {}'.format(task_id))
                        # Notify to stop execution and wait for it to end
                        task_executor.stop_execution()
                        task_executor.join(timeout)
                        return True
            finally:
                return False    

    def remove_task(self, task_id):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Move until the task is found, executed tasks can only be stopped
            for index, task in enumerate(self.__tasks_queue):        
                if task['task_id'] == task_id:
                    self.__logger.info('Removing task {}'.format(task['task_id']))
                    # Delete the task and finish
                    del self.__tasks_queue[index]
                    return True

        return False

    def promote_task(self, task_id):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Move until the task is found
            for index, task in enumerate(self.__tasks_queue):
                if task['task_id'] == task_id:
                    # Promote the task ahead if possible
                    if index > 0:
                        self.__logger.info('Promoting task {}'.format(task['task_id']))
                        self.__tasks_queue[index], self.__tasks_queue[index-1] = self.__tasks_queue[index-1], self.__tasks_queue[index]
                        return True
        return False

    def demote_task(self, task_id):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Move until the task is found
            for index, task in enumerate(self.__tasks_queue):
                if task['task_id'] == task_id:
                    # Demote the task ahead if possible
                    if index < len(self.__tasks_queue) - 1:
                        self.__logger.info('Demoting task {}'.format(task['task_id']))
                        self.__tasks_queue[index], self.__tasks_queue[index+1] = self.__tasks_queue[index+1], self.__tasks_queue[index]
                        return True
        return False

    def set_task_definition_config(self, config_path):
        # Make sure first that the task manager is not running
        if self.__is_task_manager_running:
            return False
        # Clean the old task definitions
        self.__task_definitions = {}

        self.__logger.info('Updating task manager task definitions from path {}'.format(config_path))

        # Load a task JSON config from a given path
        # Read the json file
        with open(config_path, 'r') as f:
            json_config = json.load(f)
            # Load the tasks list
            for task_info in json_config['task_definitions']:
                # Assert keys existance
                if all(name in task_info.keys() for name in REQUIRED_TASK_DEFINITION_KEYS):
                    # Create a Task def object
                    task_def = TaskDefinition(**task_info)
                    self.__logger.info('Adding task definition ' + task_def.get_task_definition_id())
                    self.__task_definitions[task_info["task_definition_id"]] = task_def 
        return True

    def is_task_manager_running(self):
        return self.__is_task_manager_running

    def start_task_manager(self):
        if self.__is_task_manager_running:
            return False

        # Re init the task manager before starting
        self.__init_task_manager()
        self.__logger.info('Starting task manager')

        self.__is_task_manager_running = True

        # Start the tasks thread
        self.__logger.info('Running task manager threads')
        self.__tasks_thread = Thread(target=self.__tasks_runner_thread)
        self.__tasks_thread.start()

        # Start the cleaner thread
        self.__cleaner_thread = Thread(target=self.__tasks_cleaner_thread)
        self.__cleaner_thread.start()

        return True

    def stop_task_manager(self):
        if not self.__is_task_manager_running:
            return False

        self.__logger.info('Stopping task manager')

        self.__is_task_manager_running = False

        self.__logger.info('Destroying task manager threads')
        # Wait for the tasks thread to end
        self.__tasks_thread.join()
        self.__tasks_thread = None

        # Wait for the cleaner thread to end
        self.__cleaner_thread.join()
        self.__cleaner_thread = None

        # Clear all the loggers from the logger manager
        self.__logger_manager.close_all_loggers()
        self.__logger = None

    def wait_for_all_tasks_to_end(self, sleep_period=DEFAULT_SLEEP_PERIOD):
        # Pooling until the task manager has no more tasks
        # This can be endless, if the task manager keeps receiving tasks
        try:
            while self.__has_more_tasks() or self.__has_more_executors_running():
                time.sleep(sleep_period)
        except:
            return False
        return True

    def wait_for_task_to_end(self, task_id, sleep_period=DEFAULT_SLEEP_PERIOD):
        # Wait for task id to show up in the tasks history
        try:
            while not task_id in self.__tasks_history.keys():
                time.sleep(sleep_period)
        except:
            return None
        # Return the task result
        return self.__tasks_history[task_id]
