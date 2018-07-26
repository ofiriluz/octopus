import pymongo
from ..access_controller import BaseAccessController
from ..access_generator import BaseAccessGenerator
import os
import json
import shutil

class FSEngine:
    def __init__(self, base_path):
        self.__base_path = base_path
    
    def get_base_path(self):
        return self.__base_path

    def create_folders(self, path):
        os.makedirs(os.path.join(self.__base_path, path))

    def delete_folders(self, path):
        os.removedirs(os.path.join(self.__base_path, path))

    def delete(self, path):
        os.remove(path)

    def write(self, path, data):
        with open(os.path.join(self.__base_path, path), 'w') as f:
            f.write(data)

    def append(self, path, data):
        with open(os.path.join(self.__base_path, path), 'a') as f:
            f.write(data)

    def read(self, path):
        with open(os.path.join(self.__base_path, path), 'r') as f:
            return f.read()

    def copy_folder(self, source, target):
        shutil.copytree(source, target)

    def copy_file(self, source, target):
        shutil.copy2(source, target)

    def load_json(self, path):
        with open(os.path.join(self.__base_path, path), 'r') as f:
            return json.load(f)

    def dump_json(self, path, json_data):
        with open(os.path.join(self.__base_path, path), 'w') as f:
            json.dump(json_data, f)

class FSController(BaseAccessController):
    def __init__(self, base_path, create_base_path=True, delete_at_end=False):
        self.__base_path = base_path
        self.__create_base_path = create_base_path
        self.__delete_at_end = delete_at_end

    def start_controller(self):
        if self.is_controller_running():
            return False

        self.__fs_engine = FSEngine(self.__base_path)

        if self.__create_base_path:
            os.makedirs(self.__fs_engine.get_base_path())

        return True

    def stop_controller(self):
        if self.is_controller_running():
            return False

        if self.__delete_at_end:
            self.__fs_engine.delete_folders('')

        self.__fs_engine = None

    def cleanup_resources(self):
        pass

    def is_controller_running(self):
        return self.__fs_engine != None
    
    def get_underlying_engine(self):
        return self.__fs_engine
        
class FSGenerator(BaseAccessGenerator):
    def __init__(self):
        super()

    def generate_access_controller(self, **kwargs):
        return FSController(**kwargs)