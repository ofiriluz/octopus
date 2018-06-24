from octopus.data_access.types.profile_question import profile_question_schema
from octopus.data_access.db.db_connection_pool import DBConnectionPool
from octopus.data_access.db.mongo_controller import MongoController, MongoGenerator
import unittest

class ProfileQuestionTests(unittest.TestCase):
    def setUp(self):
        # Init the connection pool and a controller
        pool = DBConnectionPool()
        pool.open_connection_pool(('localhost', 27017), MongoGenerator())
        pool.return_db_controller(pool.generate_db_controller(db_name='octopus'))

    def tearDown(self):
        # Close the connection pool
        pool = DBConnectionPool()
        pool.close_connection_pool()

    def test_simple_profile_question_insertion(self):
        # Create a profile question
        mutation = '''
            mutation test{
                profileMutations {
                    insertProfileQuestion(query: "Ofir Iluz", queryHints:[]) {
                        question {
                            query
                        }
                    }
                }
            }
        '''

        # Execute the query and test if the query is valid
        result = profile_question_schema.execute(mutation)
        print(str(result.errors))
        # Check if results match the given question
        self.assertEqual(result.query, "Ofir Iluz")

if __name__ == '__main__':
    unittest.main(exit=False)