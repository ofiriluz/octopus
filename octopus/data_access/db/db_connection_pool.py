from db_generator import BaseDBGenerator
from threading import Lock

DEFAULT_MAX_CONNECTION_POOL=10

# The db connection pool handles a set of controllers for DB connections
# Each controller is saved and returned to the user when used
# Once the user finishes (terminates the DB controller), The base DB controller will notify the parent pool
# The pool will remove the connection from the pool and free up a place on the pool
# The pool is thread safe and uses a db generator func, which will generate a database controller
# The database controller will be checked for base controller type (base_db_controller)
# The pool itself is not singleton but each controller has its own pool that manages it
# The DB generator should be of type db_generator to be a safe generation

class DBConnectionPool:
    def __init__(self, connection_info, db_generator, max_controller_pool=DEFAULT_MAX_CONNECTION_POOL):
        # Assert that the given is a db generator base class
        if not issubclass(type(db_generator), BaseDBGenerator):
            raise Exception('Invalid generator, cannot use the pool')
        # Assert that the connection is an ip port tuple 
        if not (type(connection_info) in [list , tuple]) or len(connection_info) != 2:
            raise Exception('Invalid connection info, must supply tuple of ip port, cannot use the pool')
        self.__connection_info = connection_info
        self.__db_generator = db_generator
        self.__max_controller_pool = DEFAULT_MAX_CONNECTION_POOL
        self.__running_controllers_pool = []
        self.__generator_mutex = Lock()
        self.__pool_running = False

    def is_pool_full(self):
        return len(self.__running_controllers_pool) == self.__max_controller_pool

    def is_pool_running(self):
        return self.__pool_running

    def generate_db_controller(self, **kwargs):
        if not self.is_pool_running():
            return None

        # Check if the pool is full
        if self.is_pool_full():
            return None
        
        # Lock the pool
        with self.__generator_mutex:
            # Generate a new db controller and assert it
            db_controller = self.__db_generator.generate_db_controller(self.__connection_info, **kwargs)
            if not db_controller or not issubclass(db_controller, BaseDBController):
                return None

            # Start the DB Controller and add it to the pool
            db_controller.start_connection()
            self.__running_controllers_pool.append(db_controller)

            # Return the controller
            return db_controller

    def return_db_controller(self, db_controller):
        if not self.is_pool_running():
            return None

        if not db_controller:
            return False

        # Find the db controller on the pool, close it and remove it from the pool
        # The comparision is done by uuid of the controller
        controller_uuid = db_controller.get_controller_uuid()
        # Lock the pool, so iteration will be thread safe
        with self.__generator_mutex:
            for index, controller in self.__running_controllers_pool:
                if controller.get_controller_uuid() == controller_uuid:
                    # Found the controller, stop it and remove it from the pool
                    controller.stop_connection()
                    controller.cleanup_resources()
                    del self.__running_controllers_pool[index]
                    return True

    def close_connection_pool(self):
        # Closes the pool and all of the controllers
        # Note that if there is a running controller instance on another part of the code, exception will probably occur
        # To prevent this, change the impl to not save the pool but only amount
        if not self.is_pool_running():
            return False

        self.__pool_running = False

        with self.__generator_mutex:
            for controller in self.__running_controllers_pool:
                controller.stop_connection()
                controller.cleanup_resources()
        self.__running_controllers_pool = []

        return True

    def open_connection_pool(self):
        if self.is_pool_running():
            return False

        self.__pool_running = True

        return True