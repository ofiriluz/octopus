import pymongo
from ..access_controller import BaseAccessController
from ..access_generator import BaseAccessGenerator
import os
import json

class GithubController(BaseAccessController):
    def __init__(self):
        # TODO, Add the api from isan AP
        self.__github_engine = None

    def start_controller(self):
        if self.is_controller_running():
            return False

        # TODO
        # self.__github_engine = ?

        return True

    def stop_controller(self):
        if self.is_controller_running():
            return False

        self.__github_engine = None

    def cleanup_resources(self):
        pass

    def is_controller_running(self):
        return self.__github_engine != None
    
    def get_underlying_engine(self):
        return self.__github_engine
        
class GithubGenerator(BaseAccessGenerator):
    def __init__(self):
        super()

    def generate_access_controller(self, **kwargs):
        return GithubController(**kwargs)