"""
Processor:
1. Receives as an input a query (username)
    processor.profile(query) 
2. Creates tasks for each access point with the username and run it
    for access_point in registered_access_points:
        query = prepare_query(access_point)
        task = create_task(access_point, query)
        run_async_task(task)
4. Each access point receives its fitting data accessor for example:
    accessors = get_access_point_accessors(task.access_point) // {"FSAccessor": X, "DBAccessor": Y, "GitAPIAccessor": Z}
    add_to_task_manager(task, accessors)
5. Depending on the mode of the ap either create a follow up query or save and profile the results
    while True:
        analysis = analyze_ap_results(results)
        if analysis.query:
            requery()
        accessors['DBAccessor'].store_results(results)
    final_results = combine_ap_results()
6. Once the task is done, receive the results and store them on using the DBAccessor
    accessors['DBAccessor'].store_results(final_results)
7. Store the query aswell
    query_accessor.store_query(query)
8. Profile the results from the access point:
    accessors = get_access_point_accessors(final_results.access_point) // {"FSAccessor": X, "DBAccessor": Y, "GitAPIAccessor": Z}
    profiler = get_profiler(final_results.access_point)
    task = create_task(profiler, final_results)
    run_async_task(task)
9. On profiling end store and return the profile results
    accessors['DBAccessor'].store_results(profiler_results)
    yield profiler_results

"""

from octopus.task_manager import TaskManager
from octopus.data_access.access_controller_pool import AccessControllerPool
from octopus.data_access.controllers.fs_controller import FSGenerator
from octopus.data_access.controllers.github_controller import GithubGenerator
from octopus.data_access.controllers.mongo_controller import MongoGenerator
from octopus.access_points.github_ap.github_access_point import GithubAccessPoint
from octopus.profiler.github import GithubProfiler
import time
import pprint
from octopus.processor.access_point_thread_task import AccessPointThreadedTask
from octopus.processor.profiler_thread_task import ProfilerThreadedTask
import os
import tempfile
from octopus.infra.logger import LoggerManager, Logger, DEBUG, INFO

GENERATORS = {
    'mongo': MongoGenerator(),
    'fs': FSGenerator(),
    'github': GithubGenerator()
}

DEFAULT_LOG_PATH = os.path.join(tempfile.gettempdir(), 'tmplogs')
DEFAULT_LOG_LEVEL = INFO

class OctopusProcessor:
    def __init__(self):
        self.__logger_manager = LoggerManager(DEFAULT_LOG_PATH)
        self.__logger = self.__logger_manager.open_logger('Processor', DEFAULT_LOG_LEVEL)
        self.__task_manager = TaskManager()
        self.__controllers_pool = AccessControllerPool()
        self.__is_processing = False
        self.__access_point_map = {
            'github': {
                'access_point': GithubAccessPoint,
                'controllers': ['mongo', 'fs', 'github'],
                'profiler': GithubProfiler
            }
        }
        self.__running_tasks_map = {}
        self.__built_profilers = {}

    def __on_profiler_done(self, id, result):
        # Check if the id of the task is in the running tasks map
        if id in self.__running_tasks_map.keys():
            # This profiling is done for this access point, save it on the finished profiled map
            self.__built_profilers[self.__running_tasks_map[id]['task_name']] = result

            # Remove the task from the running tasks
            del self.__running_tasks_map[id]


    def __on_access_point_done(self, id, result):
        # Check if the id of the task is in the running tasks map
        if id in self.__running_tasks_map.keys():
            # Save the access point results 
            self.__running_tasks_map[id]['access_point_results'] = result

            # Get the task name to use for creating the profiler
            task_name = self.__running_tasks_map[id]['task_name']

            # Create the profiler
            profiler = self.__access_point_map[task_name]['profiler']()

            # Create a profiler task
            task = self.__prepare_profile_task(result, profiler, self.__running_tasks_map[id]['controllers'])

            # Run it
            task_id = self.__add_threaded_task(task_name + "_profiler", task, self.__on_profiler_done)

            # Switch the task id to the profiler one
            self.__running_tasks_map[task_id] = self.__running_tasks_map.pop(id)

    def __add_threaded_task(self, task_name, task, callback):
        # Add the task to the task manager
        task_id = self.__task_manager.add_task(task_name, {'task_runner': task, 'task_runner_params':{}}, callback)

        # Return the task id for now
        return task_id

    def __prepare_profile_task(self, ap_results, profiler, controllers):
        # Create the profile thread task
        task = ProfilerThreadedTask(ap_results, profiler, controllers)

        # Just return it for now
        return task

    def __prepare_ap_task(self, query, access_point, controllers):
        # Create the access point thread task
        task = AccessPointThreadedTask(access_point, query, controllers)

        # Just return it for now
        return task

    def __acquire_controllers(self, controllers):
        # Create and acquire the controllers map
        controllers = {}
        for controller_key in controllers:
            # TODO -  Temp for now
            controller = None
            while not controller:
                controller = self.__controllers_pool.generate_access_controller(controller_key)
                time.sleep(0.2)
            controllers[controller_key] = controller
        return controllers

    def __release_controllers(self, controllers):
        for controller in controllers.values():
            self.__controllers_pool.return_access_controller(controller)

    def set_task_definitions_file(self, path):
        self.__task_manager.set_task_definition_config(path)

    def process_query(self, query):
        # Go over each access point and create a task for it
        # Each access point will callback here to continue the flow async

        if self.__is_processing:
            return

        self.__is_processing = True

        # Clear the old data
        self.__running_tasks_map = {}
        self.__built_profilers = {}

        # Open the connection pool if not opened yet, also set the task manager config
        if not self.__controllers_pool.is_connection_pool_open():
            self.__task_manager.set_task_definition_config('octopus/processor/octopus_task_definitions.json')
            self.__controllers_pool.open_connection_pool(GENERATORS)
            self.__task_manager.start_task_manager()

        for ap_key in self.__access_point_map.keys():
            self.__logger.info('Adding ' + ap_key)
            # Create the access point to work with
            ap = self.__access_point_map[ap_key]['access_point']()

            # Acquire the controllers from the pool
            controllers = self.__acquire_controllers(self.__access_point_map[ap_key]['controllers'])

            # Create a threaded task
            task = self.__prepare_ap_task(query, ap, controllers)

            self.__logger.info('Executing ' + ap_key)

            # Add the task to the task manager to be executed
            task_id = self.__add_threaded_task(ap_key + "_access_point", task, self.__on_access_point_done)

            # Save the returned task id with the info on the running tasks
            self.__running_tasks_map[task_id] = {
                'task_name': ap_key,
                'controllers': controllers
            }
            

        # Wait for all the tasks to end, including the forwarded profiling tasks
        self.__task_manager.wait_for_all_tasks_to_end()

        # Go over every running task and release its controllers
        for task in self.__running_tasks_map.keys():
            self.__release_controllers(self.__running_tasks_map[task]['controllers'])

        self.__is_processing = False

        # Return the final results
        return self.__built_profilers
            

if __name__ == '__main__':
    print('hello')
    processor = OctopusProcessor()
    result = processor.process_query('isan_rivkin')
    pprint.pprint(result)
