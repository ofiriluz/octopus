from task_manager import TaskMnager

def python_script_callback(result):
    print('Python Script Result')
    print(str(result))

def bash_script_callback(result):
    print('Bash Script Result')
    print(str(result))

if __name__ == '__main__':
    # Create the task manager with defaults
    task_manager = TaskMnager()

    # Set the task manager definitions
    task_manager.set_task_definition_config('D:\\Octopus\\octopus\\src\\task_manager\\tests\\task_test_definitions.json')

    # Add some tasks before starting the manager
    task_manager.add_task('PythonScriptA', ['Something'], {'input_string': 'Something'}, python_script_callback)
    task_manager.add_task('BashScriptB', [], {'output_path': 'D:\\Octopus\\octopus\\src\\task_manager\\tests\\tmp_file.json'}, bash_script_callback)

    # Start the task manager and wait for all the tasks to end
    task_manager.start_task_manager()
    task_manager.wait_for_all_tasks_to_end()

    # Stop the manager
    task_manager.stop_task_manager()