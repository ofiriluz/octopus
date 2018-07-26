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


class AddProfilerResults(graphene.Mutation):
    class Arguments:
        query_id = graphene.ID(required=True)
        profiler_result_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, query_id, profiler_result_id):
        # Get the pool singleton and use enter to generate and destroy the controller
        pool_controller_generator = DBConnectionPool() 
        with pool_controller_generator as controller:
            # Get the underlying mongo engine and perform the insertion
            mongo_engine = controller.get_underlying_engine()

            # Perform the update
            res = mongo_engine['profile-question'].update_one({'_id': ObjectId(query_id)}, {
                    '$push': {
                        'profiler_results': profiler_result_id
                    }
                })

            return AddProfilerResults(ok=(res.modified_count > 0))

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

class RemoveProfileQuestion(graphene.Mutation):
    class Arguments:
        query_id = graphene.ID(required=True)
        remove_access_points = graphene.Boolean(default_value=True)
        remove_profiler_results = graphene.Boolean(default_value=True)

    ok = graphene.Boolean()

    def mutate(self, info, query_id, remove_access_points, remove_profiler_results):
        # Get the pool singleton and use enter to generate and destroy the controller
        pool_controller_generator = DBConnectionPool() 
        with pool_controller_generator as controller:
            # Get the underlying mongo engine and perform the insertion
            mongo_engine = controller.get_underlying_engine()

            # Get the query information
            query = mongo_engine['profile-question'].find_one({'_id': ObjectId(id)})

            # Iterate on access points and remove them if allowed
            if remove_access_points:
                for access_point in query['access_points']:
                    # Remove the access point
                    mongo_engine[access_point['access_point_name']].remove({'_id': ObjectId(access_point['access_point_id'])})

            # Iterate on profiler results and remove them if allowed
            if remove_profiler_results:
                for profiler_result in query['profiler_results']:
                    # Remove the profiler result
                    mongo_engine['profiler-results'].remove({'_id': ObjectId(profiler_result)})
            
            # Erase the profile question itself
            res = mongo_engine['profile-question'].remove({'_id': ObjectId(id)})

            return RemoveProfileQuestion(ok=(res.modified_count > 0))

class ProfileQuestionMutations(graphene.ObjectType):
    insert_profile_question = InsertProfileQuestion.Field()
    add_access_point = AddAccessPoint.Field()
    add_profiler_results = AddProfilerResults.Field()
    remove_profile_question = RemoveProfileQuestion.Field()


profile_question_schema = graphene.Schema(query=ProfileQuestionQuery, mutation=ProfileQuestionMutations)

