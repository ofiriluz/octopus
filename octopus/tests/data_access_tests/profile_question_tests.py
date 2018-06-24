from octopus.data_access.types.profile_question import profile_question_schema
import unittest

class ProfileQuestionTests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_profile_question_insertion(self):
        # Create a profile question
        mutation = '''
            mutation test{
                profileMutations {
                    insertProfileQuestion(query: "Ofir Iluz", query_hints:[]) {
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