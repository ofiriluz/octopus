from .access_generator import BaseAccessGenerator
from .access_controller import BaseAccessController
from threading import Lock
import time

DEFAULT_OPEN_CONNECTION_PERIOD = 0.25
DEFAULT_MAX_CONNECTION_POOL=10

# The access connection pool handles a set of controllers for acccess to data
# Each controller is saved and returned to the user when used
# Once the user finishes (terminates the access controller), The base access controller will notify the parent pool
# The pool will remove the connection from the pool and free up a place on the pool
# The pool is thread safe and uses a access generator func, which will generate a access controller
# The access controller will be checked for base controller type (base_access_controller)
# The pool itself is singleton for the entire program
# The access generator should be of type access_generator to be a safe generation

# Have 0 open connections
# When a request to generate a new controller is given the following happens:
    # If no running controller / all running controllers in use, generate new one
    # If there is a running controller not in use, use it
# When the controller is returned, mark it as not used for further on


class AccessControllerPool:
    # Class Impl
    class __Impl:
        def __init__(self):
            self.__max_controller_pool = DEFAULT_MAX_CONNECTION_POOL
            self.__running_controllers_pool = {}
            self.__generator_mutex = Lock()
            self.__enter_exit_mutex = Lock()
            self.__current_entered_controller = None
            self.__pool_running = False

        def is_pool_full(self):
            return sum(len(l) for l in self.__running_controllers_pool.values()) == self.__max_controller_pool

        def is_pool_running(self):
            return self.__pool_running

        def get_open_access_controller(self, name):
            # This only tries to get an open controller unlike generate
            if not self.is_pool_running():
                return None

            # Check if the pool is full
            if self.is_pool_full():
                return None

            if name not in self.__running_controllers_pool.keys():
                return None

            # Lock the pool
            with self.__generator_mutex:
                for controller in self.__running_controllers_pool[name]:
                    if not controller['used']:
                        # Found a controller not in use, set used and return
                        controller['used'] = True
                        return controller['obj']
            return None

        def wait_for_open_access_controller(self, name):
            if not self.is_pool_running():
                return None

            if name not in self.__running_controllers_pool.keys():
                return None

            # Tries to wait until there is an open db controller and returns it
            while True:
                access_controller = self.get_open_access_controller(name)
                if access_controller:
                    return access_controller
                time.sleep(DEFAULT_OPEN_CONNECTION_PERIOD)
            return None

        def generate_access_controller(self, name, **kwargs):
            if not self.is_pool_running():
                return None

            # Check if the pool is full
            if self.is_pool_full():
                return None
            
            if name not in self.__access_generators.keys():
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

                # Generate a new access controller and assert it
                generator = self.__access_generators[name]
                access_controller = generator.generate_access_controller(**kwargs)
                if not access_controller or not issubclass(type(access_controller), BaseAccessController):
                    return None

                # Start the access Controller and add it to the pool
                access_controller.start_controller()
                if name not in self.__running_controllers_pool.keys():
                    self.__running_controllers_pool[name] = []
                self.__running_controllers_pool[name].append({'used': True, 'obj': access_controller})

                # Return the controller
                return access_controller

        def return_access_controller(self, name, access_controller):
            if not self.is_pool_running():
                return None

            if not access_controller:
                return False
            
            if name not in self.__running_controllers_pool.keys():
                return None

            # Find the access controller on the pool, close it and remove it from the pool
            # The comparision is done by uuid of the controller
            controller_uuid = access_controller.get_controller_uuid()
            # Lock the pool, so iteration will be thread safe
            with self.__generator_mutex:
                for controller in self.__running_controllers_pool[name]:
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
                for name in self.__running_controllers_pool.keys():
                    # Go over all the controllers and close them
                    for controller in self.__running_controllers_pool[name]:
                        controller['obj'].stop_controller()
                        controller['obj'].cleanup_resources()
            self.__running_controllers_pool = []

            return True

        def __init_pool(self, access_generators, max_controller_pool=DEFAULT_MAX_CONNECTION_POOL):
            # Assert that the given is a access generators base class
            for generator in access_generators.values():
                if not issubclass(type(generator), BaseAccessGenerator):
                    raise Exception('Invalid generator, cannot use the pool')
            self.__access_generators = access_generators
            self.__max_controller_pool = max_controller_pool

        def open_connection_pool(self, access_generators, max_controller_pool=DEFAULT_MAX_CONNECTION_POOL):
            if self.is_pool_running():
                return False

            # Init the pool
            self.__init_pool(access_generators, max_controller_pool)

            self.__pool_running = True

            return True

        def is_connection_pool_open(self):
            return self.__pool_running

    # Singleton impl
    __access_pool_instance = None
    
    def __init__(self):
        if AccessControllerPool.__access_pool_instance is None:
            AccessControllerPool.__access_pool_instance = AccessControllerPool.__Impl()
            self.__dict__['_AccessControllerPool__access_pool_instance'] = AccessControllerPool.__access_pool_instance

    def __getattr__(self, attr):
        return getattr(self.__access_pool_instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__access_pool_instance, attr, value)