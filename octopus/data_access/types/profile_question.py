import graphene
from octopus.data_access.types.common import ProfileAccessPoint
from octopus.data_access.db.db_connection_pool import DBConnectionPool
import datetime
from bson.objectid import ObjectId

class ProfileQuestion(graphene.ObjectType):
    id = graphene.ID()
    query = graphene.String()
    query_hints = graphene.List(of_type=graphene.String)
    query_host = graphene.String()
    search_time = graphene.DateTime()
    access_points = graphene.List(of_type=ProfileAccessPoint)
    profiler_results = graphene.List(of_type=graphene.ID)

# Query
class ProfileQuestionQuery(graphene.ObjectType):
    question = graphene.Field(type=ProfileQuestion)
    questions = graphene.List(
        of_type=ProfileQuestion,
        first=graphene.Int(),
        last=graphene.Int(),
        query=graphene.String())

    def resolve_question(self, info, id):
        # Get the pool singleton and use enter to generate and destroy the controller
        pool_controller_generator = DBConnectionPool() 
        with pool_controller_generator as controller:
            # Get the underlying mongo engine and perform the insertion
            mongo_engine = controller.get_underlying_engine()
            # Find the given id
            return mongo_engine['profile-question'].find_one({'_id': ObjectId(id)})

    def resolve_questions(self, info, first=None, last=None, queryEquals=None):
        # Get the pool singleton and use enter to generate and destroy the controller
        pool_controller_generator = DBConnectionPool() 
        with pool_controller_generator as controller:
            # Get the underlying mongo engine and perform the insertion
            mongo_engine = controller.get_underlying_engine()
            # Return all profile questions
            cursor = None
            if queryEquals:
                cursor = mongo_engine['profile-question'].find({'query': queryEquals})
            else:
                cursor = mongo_engine['profile-question'].find()
            if first:
                cursor.sort([{'$natural', 1}]).limit(first)
            elif last:
                cursor.sort([{'$natural', -1}]).limit(last)
            # Map each cursor item to ProfileQuestion
            results = []
            for item in cursor:
                item['id'] = item.pop('_id')
                results.append(ProfileQuestion(**item))
            return results

# Mutations
class AddAccessPoint(graphene.Mutation):
    class Arguments:
        query_id = graphene.ID(required=True)
        access_point_name = graphene.String(required=True)
        access_point_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, query_id, access_point_name, access_point_id):
        # Get the pool singleton and use enter to generate and destroy the controller
        pool_controller_generator = DBConnectionPool() 
        with pool_controller_generator as controller:
            # Get the underlying mongo engine and perform the insertion
            mongo_engine = controller.get_underlying_engine()

            # Perform the update
            res = mongo_engine['profile-question'].update_one({'_id': ObjectId(query_id)}, {
                    '$push': {
                        'access_points': {
                            'access_point_name': access_point_name, 
                            'access_point_id': access_point_id
                        }
                    }
                })

            return AddAccessPoint(ok=(res.modified_count > 0))


class InsertProfileQuestion(graphene.Mutation):
    class Arguments:
        query = graphene.String(required=True)
        query_host = graphene.String(default_value='')
        query_hints = graphene.List(of_type=graphene.String, default_value=[])

    question = graphene.Field(type=ProfileQuestion)

    def mutate(self, info, query, query_host, query_hints):
        # Get the pool singleton and use enter to generate and destroy the controller
        pool_controller_generator = DBConnectionPool() 
        with pool_controller_generator as controller:
            # Get the underlying mongo engine and perform the insertion
            mongo_engine = controller.get_underlying_engine()
            question = {
                'query': query,
                'query_hints': query_hints,
                'query_host': query_host,
                'search_time': str(datetime.datetime.now()),
                'access_points': [],
                'profiler_results': []
            }

            # Insert the doc and get the id
            question['id'] = mongo_engine['profile-question'].insert_one(question).inserted_id

            # Remove the mongo _id for population
            del question['_id']

            # Populate profile question
            pq = ProfileQuestion(**question)

            # Return it as the object described
            return InsertProfileQuestion(question=pq)


class ProfileQuestionMutations(graphene.ObjectType):
    insert_profile_question = InsertProfileQuestion.Field()
    add_access_point = AddAccessPoint.Field()


profile_question_schema = graphene.Schema(query=ProfileQuestionQuery, mutation=ProfileQuestionMutations)

