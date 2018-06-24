from .db_generator import BaseDBGenerator
from .db_controller import BaseDBController
from threading import Lock
import time

DEFAULT_OPEN_CONNECTION_PERIOD = 0.25
DEFAULT_MAX_CONNECTION_POOL=10

# The db connection pool handles a set of controllers for DB connections
# Each controller is saved and returned to the user when used
# Once the user finishes (terminates the DB controller), The base DB controller will notify the parent pool
# The pool will remove the connection from the pool and free up a place on the pool
# The pool is thread safe and uses a db generator func, which will generate a database controller
# The database controller will be checked for base controller type (base_db_controller)
# The pool itself is singleton for the entire program
# The DB generator should be of type db_generator to be a safe generation

# Have 0 open connections
# When a request to generate a new controller is given the following happens:
    # If no running controller / all running controllers in use, generate new one
    # If there is a running controller not in use, use it
# When the controller is returned, mark it as not used for further on


class DBConnectionPool:
    # Class Impl
    class __Impl:
        def __init__(self):
            self.__max_controller_pool = DEFAULT_MAX_CONNECTION_POOL
            self.__running_controllers_pool = []
            self.__generator_mutex = Lock()
            self.__pool_running = False

        def is_pool_full(self):
            return len(self.__running_controllers_pool) == self.__max_controller_pool

        def is_pool_running(self):
            return self.__pool_running

        def get_open_db_controller(self):
            # This only tries to get an open controller unlike generate
            if not self.is_pool_running():
                return None

            # Check if the pool is full
            if self.is_pool_full():
                return None

            # Lock the pool
            with self.__generator_mutex:
                for controller in self.__running_controllers_pool:
                    if not controller['used']:
                        # Found a controller not in use, set used and return
                        controller['used'] = True
                        return controller['obj']
            return None

        def wait_for_open_db_connection(self):
            # Tries to wait until there is an open db controller and returns it
            while True:
                db_controller = self.get_open_db_controller()
                if db_controller:
                    return db_controller
                time.sleep(DEFAULT_OPEN_CONNECTION_PERIOD)
            return None

        def generate_db_controller(self, **kwargs):
            if not self.is_pool_running():
                return None

            # Check if the pool is full
            if self.is_pool_full():
                return None
            
            # Lock the pool
            with self.__generator_mutex:
                # First check if there is a controller not in use
                # If there is, return it and set it to be used
                for controller in self.__running_controllers_pool:
                    if not controller['used']:
                        # Found a controller not in use, set used and return
                        controller['used'] = True
                        return controller['obj']

                # Generate a new db controller and assert it
                db_controller = self.__db_generator.generate_db_controller(self.__connection_info, **kwargs)
                if not db_controller or not issubclass(type(db_controller), BaseDBController):
                    return None

                # Start the DB Controller and add it to the pool
                db_controller.start_controller()
                self.__running_controllers_pool.append({'used': True, 'obj': db_controller})

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
                for controller in self.__running_controllers_pool:
                    if controller['obj'].get_controller_uuid() == controller_uuid:
                        # Found the controller, un-use it, do not close it
                        controller['used'] = False
                        return True

        def close_connection_pool(self):
            # Closes the pool and all of the controllers
            # Note that if there is a running controller instance on another part of the code, exception will probably occur
            # To prevent this, change the impl to not save the pool but only amount
            if not self.is_pool_running():
                return False

            self.__pool_running = False

            with self.__generator_mutex:
                # Go over all the controllers and close them
                for controller in self.__running_controllers_pool:
                    controller['obj'].stop_controller()
                    controller['obj'].cleanup_resources()
            self.__running_controllers_pool = []

            return True

        def __init_pool(self, connection_info, db_generator, max_controller_pool=DEFAULT_MAX_CONNECTION_POOL):
            # Assert that the given is a db generator base class
            if not issubclass(type(db_generator), BaseDBGenerator):
                raise Exception('Invalid generator, cannot use the pool')
            # Assert that the connection is an ip port tuple 
            if not (type(connection_info) in [list , tuple]) or len(connection_info) != 2:
                raise Exception('Invalid connection info, must supply tuple of ip port, cannot use the pool')
            self.__connection_info = connection_info
            self.__db_generator = db_generator
            self.__max_controller_pool = max_controller_pool

        def open_connection_pool(self, connection_info, db_generator, max_controller_pool=DEFAULT_MAX_CONNECTION_POOL):
            if self.is_pool_running():
                return False

            # Init the pool
            self.__init_pool(connection_info, db_generator, max_controller_pool)

            self.__pool_running = True

            return True

    # Singleton impl
    __db_pool_instance = None
    
    def __init__(self):
        if DBConnectionPool.__db_pool_instance is None:
            DBConnectionPool.__db_pool_instance = DBConnectionPool.__Impl()
            self.__dict__['_DBConnectionPool__db_pool_instance'] = DBConnectionPool.__db_pool_instance

    def __getattr__(self, attr):
        return getattr(self.__db_pool_instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__db_pool_instance, attr, value)
