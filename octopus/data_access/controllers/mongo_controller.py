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
from ..access_controller import BaseAccessController
from ..access_generator import BaseAccessGenerator


class MongoController(BaseAccessController):
    def __init__(self, connection_info, db_name, db_username=None, db_password=None):
        self.__db_username = db_username
        self.__db_password = db_password
        self.__db_name = db_name
        self.__connection_host = connection_info[0]
        self.__connection_port = connection_info[1]
        self.__mongo_connection = None

    def start_controller(self):
        if self.is_controller_running():
            return False

        # Create a mongo connection
        self.__mongo_connection = pymongo.MongoClient(host=self.__connection_host, 
                                                      port=self.__connection_port,
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
        

class MongoGenerator(BaseAccessGenerator):
    def __init__(self):
        super()

    def generate_access_controller(self, **kwargs):
        return MongoController(**kwargs)