from octopus.task_manager import TaskThreadRunner

class ProfilerThreadedTask(TaskThreadRunner):
    def __init__(self, ap_results, profiler, controllers):
        self.__wrapped_profiler = profiler
        self.__ap_results = ap_results
        self.__controllers = controllers
        self.__is_profiler_running = False

    def run(self, logger, **kwargs):
        if self.__is_profiler_running:
            return None

        logger.info('Starting profiler task')

        return self.__wrapped_profiler.do_profiling(logger, self.__ap_results, self.__controllers)

    def stop(self):
        pass