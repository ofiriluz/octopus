from threading import Thread, Event, Lock
import os
import subprocess

class TaskExecutor:
    def __init__(self, task, task_definition, logger, write_output_to_log=True):
        self.__task = task
        self.__task_definition = task_definition
        self.__task_execution_thread = None
        self.__task_execution_mutex = Lock()
        self.__is_running = False
        self.__logger = logger
        self.__execution_process = None
        self.__write_output_to_log = write_output_to_log
        self.__stdout_logs = []

    def __stdout_log_callback(self, msg):
        # Save stdout to later be used
        self.__stdout_logs.append(msg)
        # Write to log if allowed
        if self.__write_output_to_log:
            self.__logger.debug(msg)

    def __stderr_log_callback(self, msg):
        # Write to log if allowed
        if self.__write_output_to_log:
            self.__logger.error(msg)

    def __execution_log_stream_thread(self, stream_func, log_func, thread_event):
        # Go over the given stream
        for out_line in iter(stream_func, ""):
            # Stop execution if executor finishes
            if not self.__is_running or thread_event.is_set():
                return
            # Log it on the given function
            log_func(out_line)

    def __get_console_piped_result(self):
        # Create a fully textual log
        log = '\n'.join(self.__stdout_logs)

        output_pipe = self.__task_definition.get_output_pipe()
        # Check if a start word was given
        if 'start' in output_pipe['pipe_params'].keys():
            # Find it from the end and split up until that
            index = log.rfind(output_pipe['pipe_params']['start'])
            if index > 0:
                log = log[index+len(log.rfind(output_pipe['pipe_params']['start'])):]
        
        return log

    def __get_file_piped_result(self):
        # Check if the given file path exists
        output_pipe = self.__task_definition.get_output_pipe()

        # Check if the parsed path is in the pipe params
        if 'path' in output_pipe['pipe_params'].keys():
            path = output_pipe['pipe_params']['path']
            # Check if the path exists
            if os.path.exists(path):
                # Open the path file and read it and send it back to the user
                f = open(path, 'r')
                return f.readlines()
        return None

    def __get_piped_result(self):
        output_pipe = self.__task_definition.get_output_pipe()
        # Get the output pipe type
        pipe_type = output_pipe['pipe']
        if pipe_type == 'console':
            return self.__get_console_piped_result()
        elif pipe_type == 'file':
            return self.__get_file_piped_result()
        return None

    def __execution_thread(self):
        # Assert that the execution script exists
        task_execution_script = self.__task_definition.get_task_execution_script()

        if os.path.exists(task_execution_script):
            # Prepare the process params with the first being the script to run
            script_params = [self.__task_definition.get_task_shell_executor(), 
                            self.__task_definition.get_task_execution_script()] + self.__task['task_execution_params']

            # Create the sub process 
            # Lock until the process gets into wait state to avoid collision with stop the execution
            self.__task_execution_mutex.acquire()

            self.__logger.info('Executing task process {}'.format(self.__task['task_id']))
            self.__execution_process = subprocess.Popen(script_params, 
                                                        shell=True,
                                                        stdout=subprocess.PIPE,
                                                        universal_newlines=True)

            stdout_thread = stderr_thread = None
            stream_event = Event()

            # Start log monitoring thread for stdout and stderr
            self.__logger.info('Starting log threads for task {}'.format(self.__task['task_id']))
            stdout_thread = Thread(self.__execution_log_stream_thread, 
                                    (self.__execution_process.stdout.readline, self.__stdout_log_callback, stream_event,))
            stdout_thread.start()

            stderr_thread = Thread(self.__execution_log_stream_thread, 
                                    (self.__execution_process.stderr.readline, self.__stderr_log_callback, stream_event,))
            stderr_thread.start()

            # Unlock the mutex
            self.__task_execution_mutex.release()

            # Wait for the process to end
            self.__execution_process.wait()

            # Close the log threads
            stream_event.set()
            stdout_thread.join()
            stderr_thread.join()

            if self.__is_running:
                # Get the final output
                self.__logger.info('Retrieving task result for task {}'.format(self.__task['task_id']))
                result = self.__get_piped_result()

                # Callback with the result of the process
                if self.__task['task_callback'] and callable(self.__task['task_callback']): 
                    self.__task['task_callback'](result)

            # Cleanup
            self.__is_running = False
            self.__execution_process = None
            

    def start_execution(self):
        if self.__is_running:
            return False

        self.__is_running = True

        # Create and run the execution thread
        self.__task_execution_thread = Thread(self.__execution_thread)
        self.__task_execution_thread.start()

    def stop_execution(self):
        if not self.__is_running:
            return False

        self.__is_running = False

        # Stop the execution and wait
        self.__execution_process.kill()
        self.__task_execution_thread.join()

    def is_running(self):
        return self.__is_running

    def is_ready_to_execute(self):
        return self.__task_definition is not None and self.__task is not None and not self.__is_running