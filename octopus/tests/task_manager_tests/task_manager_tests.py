from octopus.task_manager import TaskManager
import unittest
from octopus.task_manager.thread import TaskThreadRunner

class DummyTaskThreadRunner(TaskThreadRunner):
    def __init__(self):
        pass

    def run(self, logger, **kwargs):
        logger.info('hello world')
        logger.info(kwargs['test'])
        return '{\"Test\":\"ABC\"}'

    def stop(self):
        pass


class TaskManagerTests(unittest.TestCase):
    def setUp(self):
        # Create the task manager with defaults
        self.task_manager = TaskManager()

        # Set the task manager definitions
        self.task_manager.set_task_definition_config('octopus/tests/task_manager_tests/task_test_definitions.json')

        # Start the task manager
        self.task_manager.start_task_manager()

    def tearDown(self):
        # Stop the task manager
        self.task_manager.stop_task_manager()

    def python_script_callback(self, result):
        self.assertEqual(result, '{\"Test\":\"ABC\"}')

    def bash_script_callback(self, result):
        self.assertEqual(result, '{\"Test\":\"ABC\"}')

    def thread_callback(self, result):
        self.assertEqual(result, '{\"Test\":\"ABC\"}')

    def test_sync_task_manager_tasks(self):
        # Add some tasks before starting the manager
        first_task_id = self.task_manager.add_task('PythonScriptA', {'task_execution_params': ['Something'], 'task_extra_params': {'input_string': 'Something'}})
        second_task_id = self.task_manager.add_task('BashScriptB', {'task_execution_params': [], 'task_extra_params': {'output_path': 'octopus/tests/task_manager_tests/tmp_file.json'}})
        third_task_id = self.task_manager.add_task('ThreadExecutionC', {'task_runner': DummyTaskThreadRunner(), 'task_runner_params': {'test': 123}})
        
        first_task_result = self.task_manager.wait_for_task_to_end(first_task_id)
        second_task_result = self.task_manager.wait_for_task_to_end(second_task_id)
        third_task_result = self.task_manager.wait_for_task_to_end(third_task_id)
        
        # Assert that the results are as expected
        self.assertEqual(first_task_result['task_result'], '{\"Test\":\"ABC\"}')
        self.assertEqual(second_task_result['task_result'], '{\"Test\":\"ABC\"}')
        self.assertEqual(third_task_result['task_result'], '{\"Test\":\"ABC\"}')

    def test_async_task_manager_tasks(self):
        # Add some tasks before starting the manager
        self.task_manager.add_task('PythonScriptA', {'task_execution_params': ['Something'], 'task_extra_params': {'input_string': 'Something'}}, self.python_script_callback)
        self.task_manager.add_task('BashScriptB', {'task_execution_params': [], 'task_extra_params': {'output_path': 'octopus/tests/task_manager_tests/tmp_file.json'}}, self.bash_script_callback)
        self.task_manager.add_task('ThreadExecutionC', {'task_runner': DummyTaskThreadRunner(), 'task_runner_params': {'test': 123}}, self.thread_callback)

        # Start the task manager and wait for all the tasks to end
        self.task_manager.wait_for_all_tasks_to_end()

if __name__ == '__main__':
    unittest.main(exit=False)