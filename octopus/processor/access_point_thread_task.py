from octopus.task_manager import TaskThreadRunner

class AccessPointThreadedTask(TaskThreadRunner):
    def __init__(self, access_point, query, controllers):
        self.__wrapped_ap = access_point
        self.__query = query
        self.__controllers = controllers
        self.__is_ap_running = False

    def run(self, logger, **kwargs):
        if self.__is_ap_running:
            return None

        logger.info('Starting access point task')

        return self.__wrapped_ap.resolve_query(logger, self.__query, self.__controllers)

    def stop(self):
        pass