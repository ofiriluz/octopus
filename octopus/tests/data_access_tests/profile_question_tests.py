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

    def add_profile_question(self, query, host):
        # Create a profile question
        mutation = '''
            mutation profileQuestionInsertion {
                insertProfileQuestion(query: "%s", queryHints:[], queryHost: "%s") {
                    question {
                        id
                        query
                    }
                }
            }
        ''' % (query, host)

        # Execute the query and test if the query is valid
        return profile_question_schema.execute(mutation)

    def remove_profile_question(self, id):
        mutation = '''
            mutation removeProfileQuestion {
                removeProfileQuestion(queryId: "%s") {
                    ok
                }
            }
        ''' % (id)

        return profile_question_schema.execute(mutation)

    def add_access_point(self, id, ap_name, ap_id):
        mutation = '''
            mutation profileQuestionAPAdd {
                addAccessPoint(queryId: "%s", accessPointName: "%s", accessPointId: "%s") {
                    ok
                }
            }
        ''' % (id, ap_name, ap_id)

        # Execute the query and test if the query is valid
        return profile_question_schema.execute(mutation)

    def add_profiler_result(self, id, pr_id):
        mutation = '''
            mutation profileQuestionPRAdd {
                addProfilerResults(queryId: "%s", profileResultId: "%s") {
                    ok
                }
            }
        ''' % (id, pr_id)

        # Execute the query and test if the query is valid
        return profile_question_schema.execute(mutation)

    def get_profile_question(self, id):
        query = '''
            query getProfileQuestion {
                question(id: %s) {
                    id
                }     
            }
        '''.format(id)

        # Execute the query and test if the query is valid
        return profile_question_schema.execute(query)

    def get_profile_questions(self, first=None, last=None, query=None):
        query = '''
            query getManyProfileQuestion {
                questions(last: %d, first: %d, query: %s) {
                    id
                }     
            }
        '''.format(last, first, query)

        # Execute the query and test if the query is valid
        return profile_question_schema.execute(query)

    def test_add_profile_results(self):
        # Execute the query and test if the query is valid
        result = self.add_profile_question('Ofir Iluz', '1.1.1.1')
        self.assertIsNone(result.errors)

        # Execute the query and test if the query is valid
        id = result.data['insertProfileQuestion']['question']['id']
        result = self.add_profiler_result(id, '123')

        # Check if results match the given question
        self.assertIsNone(result.errors)
        self.assertEqual(result.data['addProfileResults']['ok'], True)        

        # Remove the added profile question
        result = self.remove_profile_question(id)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data['removeAccessPoint']['ok'], True)

    def test_remove_profile_question(self):
        # Execute the query and test if the query is valid
        result = self.add_profile_question('Ofir Iluz', '1.1.1.1')
        self.assertIsNone(result.errors)        

        question_id = result.data['insertProfileQuestion']['question']['id'] 

        # Remove the added profile question
        result = self.remove_profile_question(question_id)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data['removeAccessPoint']['ok'], True)

    def test_profile_question_access_point_add(self):
        # Execute the query and test if the query is valid
        result = self.add_profile_question('Ofir Iluz', '1.1.1.1')
        self.assertIsNone(result.errors)

        # Execute the query and test if the query is valid
        question_id = result.data['insertProfileQuestion']['question']['id']
        result = self.add_access_point(question_id, 'twitter', '123')

        # Check if results match the given question
        self.assertIsNone(result.errors)
        self.assertEqual(result.data['addAccessPoint']['ok'], True)

        # Remove the added profile question
        result = self.remove_profile_question(id)
        self.assertIsNone(result.errors)
        self.assertEqual(result.data['removeAccessPoint']['ok'], True)

    def test_profile_question_insertion(self):
        # Execute the query and test if the query is valid
        result = self.add_profile_question('Ofir Iluz', '1.1.1.1')
        
        # Check if results match the given question
        self.assertIsNone(result.errors)
        self.assertEqual(result.data['insertProfileQuestion']['question']['query'], "Ofir Iluz")

if __name__ == '__main__':
    unittest.main(exit=False)