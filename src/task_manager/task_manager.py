from threading import Lock, Event, Thread
from task_definition import TaskDefinition
from task_executor import TaskExecutor
import time
import json
import uuid

REQUIRED_TASK_DEFINITION_KEYS = ['task_defintion_id', 'task_execution_script', 'task_params', 'task_output_pipe']
DEFAULT_MAX_RUNNING_TASKS = 5
DEFAULT_POOL_TIMEOUT = 10

class TaskManager:
    def __init__(self, max_running_tasks=DEFAULT_MAX_RUNNING_TASKS, pool_timeout=DEFAULT_POOL_TIMEOUT):
        self.__tasks_queue = []
        self.__task_executors = []
        self.__tasks_mutex = Lock() 
        self.__tasks_pool_event = Event()
        self.__is_task_manager_running = False
        self.__tasks_history = []
        self.__task_definitions = {}
        self.__max_running_tasks = max_running_tasks
        self.__pool_timeout = pool_timeout
        self.__tasks_thread = None
        self.__cleaner_thread = None

    def __init_task_manager(self):
        # Reset all the lists
        self.__tasks_queue = self.__task_executors = self.__tasks_history = []
        self.__task_definitions = {}
        # Reset the threads, shouldnt be running here
        self.__tasks_thread = self.__cleaner_thread = None

    def __execute_task(self, task, task_defintion):
        # Create the task executor
        task_executor = TaskExecutor(task, task_defintion)

        # Check if its ready to be executed
        if task_executor.is_ready_to_execute():
            # Run it, will create a new thread inside
            task_executor.start_execution()

            # Sace the executor
            self.__task_executors.append(task_executor)

            return True

        return False

    def __is_task_pool_full(self):
        return len(self.__task_executors) == self.__max_running_tasks

    def __pop_next_task(self):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Check if there is a task to pop
            if len(self.__task_executors) > 0:
                # Pop and return the task
                return self.__task_executors.pop(0)
        return None

    def __retrieve_task_definition(self, task_definition_id):
        # Return the task defintion if exists
        if task_definition_id in self.__task_definitions.keys():
            return self.__task_definitions[task_definition_id]
        return None

    def __tasks_cleaner_thread(self):
        while self.__is_task_manager_running:
            indices_to_remove = []
            # Check if any task is done
            for index, task_executor in enumerate(self.__task_executors):
                if not task_executor.is_running():
                    indices_to_remove.append(index)

            # Remove the indexes
            with self.__tasks_mutex:
                self.__task_executors = [i for j, i in enumerate(self.__task_executors) if j not in indices_to_remove]
            time.sleep(1)
                    
    def __tasks_runner_thread(self):
        # Run untill the manager is stopped
        while self.__is_task_manager_running:
            # If the pool is full, wait for a trigger, with timeout incase a task has failed
            if self.__is_task_pool_full():
                self.__tasks_pool_event.wait(timeout=self.__pool_timeout)

            # Get the next task to deploy
            task = self.__pop_next_task()
            if task:
                # Get the task definition of this task
                task_def = self.__retrieve_task_definition(task['task_definition_id'])
                if task_def:
                    # Execute the task
                    self.__execute_task(task, task_def)
            # Sleep to not overrun the task manager
            time.sleep(0.1)
                
    def add_task(self, task_definition_id, task_execution_params_list, task_extra_params, task_callback=None):
        # Lock the tasks mutex
        with self.__tasks_mutex:
            # Get the task definition
            task_def = self.__retrieve_task_definition(task_definition_id)
            # Assert that execution params are specificly a list 
            if type(task_execution_params_list) is in [list, tuple]:
                # Create and add the task
                # Generate a task id
                task_id = str(uuid.uuid4())
                # Create the task dict
                task = {
                    "task_id": task_id,
                    "task_definition_id": task_definition_id,
                    "task_execution_params": task_execution_params,
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
                for index, task_executor in enumerate(self.__task_executors):
                    # Find the executor
                    if task_executor.get_task()['task_id'] == task_id:
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
                        self.__tasks_queue[index], self.__tasks_queue[index+1] = self.__tasks_queue[index+1], self.__tasks_queue[index]
                        return True
        return False

    def set_task_definition_config(self, config_path):
        # Make sure first that the task manager is not running
        if self.__is_task_manager_running:
            return False
        # Clean the old task definitions
        self.__task_definitions = []

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
                    self.__task_definitions[task_info["task_definition_id"]] = task_def
                    
        return True

    def is_task_manager_running(self):
        return self.__is_task_manager_running

    def start_task_manager(self):
        if self.__is_task_manager_running:
            return False

        # Re init the task manager before starting
        self.__init_task_manager()

        self.__is_task_manager_running = True

        # Start the tasks thread
        self.__tasks_thread = Thread(self.__tasks_runner_thread)
        self.__tasks_thread.start()

        # Start the cleaner thread
        self.__cleaner_thread = Thread(self.__tasks_cleaner_thread)
        self.__cleaner_thread.start()

        return True

    def stop_task_manager(self):
        if not self.__is_task_manager_running:
            return False

        self.__is_task_manager_running = False

        # Wait for the tasks thread to end
        self.__tasks_thread.join()
        self.__tasks_thread = None

        # Wait for the cleaner thread to end
        self.__cleaner_thread.join()
        self.__cleaner_thread = None


