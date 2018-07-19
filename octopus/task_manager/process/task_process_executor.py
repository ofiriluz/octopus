from threading import Thread, Event, Lock
import os
import subprocess
import datetime
from octopus.task_manager.base_task_executor import BaseTaskExecutor

class TaskProcessExecutor(BaseTaskExecutor):
    def __init__(self, task, task_definition, logger, write_output_to_log=True):
        super().__init__(task, task_definition, logger)
        self.__task_execution_thread = None
        self.__task_execution_mutex = Lock()
        self.__is_running = False
        self.__execution_process = None
        self.__write_output_to_log = write_output_to_log
        self.__stdout_logs = []
        self.__task_result = None
        self.__task_start_time = None
        self.__task_end_time = None

    def __stdout_log_callback(self, msg):
        # Save stdout to later be used
        self.__stdout_logs.append(msg)
        # Write to log if allowed
        if self.__write_output_to_log:
            self.get_task_executor_logger().debug(msg)

    def __stderr_log_callback(self, msg):
        # Write to log if allowed
        if self.__write_output_to_log:
            self.get_task_executor_logger().error(msg)

    def __execution_log_stream_thread(self, stream_func, log_func, thread_event):
        # Go over the given stream
        for out_line in iter(stream_func, ""):
            # Stop execution if executor finishes
            if not self.__is_running or thread_event.is_set():
                return
            # Log it on the given function
            log_func(out_line.strip())

    def __get_console_piped_result(self, output_pipe):
        # Create a fully textual log
        log = '\n'.join(self.__stdout_logs)

        # Check if a start word was given
        if 'start' in output_pipe['pipe_params'].keys():
            # Find it from the end and split up until that
            index = log.rfind(output_pipe['pipe_params']['start'])
            if index > 0:
                log = log[index + len(output_pipe['pipe_params']['start']):].strip()
        
        return log

    def __get_file_piped_result(self, output_pipe):
        # Check if the parsed path is in the pipe params
        if 'path' in output_pipe['pipe_params'].keys():
            path = output_pipe['pipe_params']['path']
            # Check if the path exists
            if os.path.exists(path):
                # Open the path file and read it and send it back to the user
                with open(path, 'r') as f:
                    return '\n'.join(line.strip() for line in f.readlines())
        return None

    def __get_piped_result(self):
        output_pipe = self.get_task_definition().get_output_pipe(self.get_task()['task_params']['task_extra_params'])
        # Get the output pipe type
        pipe_type = output_pipe['pipe']
        if pipe_type == 'console':
            return self.__get_console_piped_result(output_pipe)
        elif pipe_type == 'file':
            return self.__get_file_piped_result(output_pipe)
        return None

    def __execution_thread(self):
        self.get_task_executor_logger().debug('Execution thread started for task ' + self.get_task()['task_id'])
        # Assert that the execution script exists
        task_execution_script = self.get_task_definition().get_task_execution_script()

        try:
            if os.path.exists(task_execution_script):
                # Prepare the process params with the first being the script to run
                script_params = [self.get_task_definition().get_task_shell_executor(), 
                                self.get_task_definition().get_task_execution_script()] + self.get_task()['task_params']['task_execution_params']

                # Create the sub process 
                # Lock until the process gets into wait state to avoid collision with stop the execution
                self.__task_execution_mutex.acquire()

                self.get_task_executor_logger().debug('Executing task process {}'.format(self.get_task()['task_id']))
                # Save the task start time
                self.__task_start_time = datetime.datetime.now()

                # Start the task
                self.__execution_process = subprocess.Popen(script_params, 
                                                            shell=True,
                                                            stdout=subprocess.PIPE,
                                                            stderr=subprocess.PIPE,
                                                            universal_newlines=True)

                stdout_thread = stderr_thread = None
                stream_event = Event()

                # Start log monitoring thread for stdout and stderr
                self.get_task_executor_logger().debug('Starting log threads for task {}'.format(self.get_task()['task_id']))
                stdout_thread = Thread(target=self.__execution_log_stream_thread, 
                                        args=(self.__execution_process.stdout.readline, self.__stdout_log_callback, stream_event,))
                stdout_thread.start()

                stderr_thread = Thread(target=self.__execution_log_stream_thread, 
                                        args=(self.__execution_process.stderr.readline, self.__stderr_log_callback, stream_event,))
                stderr_thread.start()

                # Unlock the mutex
                self.__task_execution_mutex.release()

                # Wait for the process to end
                self.__execution_process.wait()

                # Close the log threads
                stream_event.set()
                stdout_thread.join()
                stderr_thread.join()

                # Save the task end time
                self.__task_end_time = datetime.datetime.now()

                if self.__is_running:
                    # Get the final output
                    self.get_task_executor_logger().debug('Retrieving task result for task {}'.format(self.get_task()['task_id']))
                    self.__task_result = self.__get_piped_result()

                    # Callback with the result of the process
                    if self.get_task()['task_callback'] and callable(self.get_task()['task_callback']): 
                        self.get_task()['task_callback'](self.__task_result)
                else:
                    self.__task_start_time = self.__task_end_time = datetime.datetime.now()
                    self.__task_result = 'Error: Script path does not exist'
        except:
            self.__task_start_time = self.__task_end_time = datetime.datetime.now()
            self.__task_result = 'Error: Process Exception'
        finally:
            # Cleanup
            self.__is_running = False
            self.__execution_process.stdout.close()
            self.__execution_process.stderr.close()
            self.__execution_process = None
            

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
        self.__execution_process.kill()
        self.__task_execution_thread.join()

    def is_running(self):
        return self.__is_running

    def is_ready_to_execute(self):
        return self.get_task_definition() is not None and self.get_task() is not None and not self.__is_running

    def get_task_result(self):
        return self.__task_result

    def get_task_duration(self):
        return self.__task_end_time - self.__task_start_time