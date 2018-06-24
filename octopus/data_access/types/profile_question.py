import graphene
from octopus.data_access.types.common import ProfileAccessPoint
from octopus.data_access.db.db_connection_pool import DBConnectionPool
import datetime

class ProfileQuestion(graphene.ObjectType):
    id = graphene.ID()
    query = graphene.String()
    query_hints = graphene.List(of_type=graphene.String)
    query_host = graphene.String()
    search_time = graphene.DateTime()
    access_points = graphene.List(of_type=ProfileAccessPoint)
    profiler_results = graphene.List(of_type=graphene.ID)

class ProfileQuestionQuery(graphene.ObjectType):
    profile_question = graphene.Field(type=ProfileQuestion)

    def resolve_profile_question(self, info, id):
        # TODO
        pass

# Mutations
class InsertProfileQuestion(graphene.Mutation):
    class Arguments:
        query = graphene.String(required=True)
        query_host = graphene.String(default_value='')
        query_hints = graphene.List(of_type=graphene.String, default_value=[])

    question = graphene.Field(type=ProfileQuestion)

    def mutate(self, info, query, query_host, query_hints):
        # Get the singleton DB Connection pool
        pool = DBConnectionPool()

        # This assuems that the program already created a conneection 
        controller = pool.wait_for_open_db_connection()

        # Get the underlying mongo engine and perform the insertion
        mongo_engine = controller.get_underlying_engine()
        question = {
            'query': query,
            'query_hints': query_hints,
            'query_host': query_host,
            'search_time': datetime.datetime.now(),
            'access_points': [],
            'profiler_results': []
        }

        # Insert the doc and get the id
        question['id'] = mongo_engine['profile-question'].insert_one(question).inserted_id

        # Return it as the object described
        return ProfileQuestion(question)

class ProfileQuestionMutations(graphene.ObjectType):
    insert_profile_question = InsertProfileQuestion.Field()

class ProfileQuestionMutator(graphene.ObjectType):
    profile_mutations = graphene.Field(type=ProfileQuestionMutations)

    def resolve_profile_mutations(self, *_):
        return ProfileQuestionMutations()


profile_question_schema = graphene.Schema(query=ProfileQuestionQuery, mutation=ProfileQuestionMutator)

