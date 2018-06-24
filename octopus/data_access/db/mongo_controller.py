# Mongo controller has the following:
# The base mongoengine defining the connection
# The following Documents defining the main mongo docs and a document for each access point
# An upper level wrapper defining the graphql layer, so that it is seperated from the db impl for later usage maybe with neo4j

# Flow:
    # Open a controller via the pool
    # Create a query via graphQL
    # Execute the graphql query, which will be transformed to mongo controlled document
    # 

import pymongo
from .db_controller import BaseDBController
from .db_generator import BaseDBGenerator


class MongoController(BaseDBController):
    def __init__(self, connection_info, db_name, db_username=None, db_password=None):
        super().__init__(connection_info)

        self.__db_username = db_username
        self.__db_password = db_password
        self.__db_name = db_name
        self.__mongo_connection = None

    def start_controller(self):
        if self.is_controller_running():
            return False

        # Create a mongo connection
        self.__mongo_connection = pymongo.MongoClient(host=self.get_controller_host(), 
                                                      port=self.get_controller_port(),
                                                      username=self.__db_username,
                                                      password=self.__db_password)

        return True

    def stop_controller(self):
        if self.is_controller_running():
            return False

        # Destroy the mongo connection
        self.__mongo_connection.close()
        self.__mongo_connection = None

    def cleanup_resources(self):
        pass

    def is_controller_running(self):
        return self.__mongo_connection != None
    
    def get_underlying_engine(self):
        return self.__mongo_connection[self.__db_name]


class MongoGenerator(BaseDBGenerator):
    def __init__(self):
        super()

    def generate_db_controller(self, connection_info, **kwargs):
        return MongoController(connection_info, **kwargs)