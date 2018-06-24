import graphene
from octopus.data_access.types.common import ProfileAccessPoint

class ProfileHintType(graphene.Enum):
    REGEX = 1
    HAMMING = 2

class ProfileQuestionHint(graphene.InputObjectType):
    hint_string = graphene.NonNull(graphene.String)
    # hint_type = graphene.InputField(ProfileHintType)

class ProfileQuestionHints(graphene.InputObjectType):
    hints = graphene.List(of_type=ProfileQuestionHint)

class ProfileQuestion(graphene.ObjectType):
    query = graphene.String()
    query_hints = graphene.List(of_type=ProfileQuestionHint)
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
        query_hints = graphene.Argument(ProfileQuestionHints)

    question = graphene.Field(type=ProfileQuestion)

    # @staticmethod
    def mutate(self, info, query, query_hints):
        print('Hello')
        print(str(info))
        print(str(query))
        print(str(query_hints))
        return ProfileQuestion()

class ProfileQuestionMutations(graphene.ObjectType):
    insert_profile_question = InsertProfileQuestion.Field()

class ProfileQuestionMutator(graphene.ObjectType):
    profile_mutations = graphene.Field(type=ProfileQuestionMutations)

    def resolve_profile_mutations(self, *_):
        return ProfileQuestionMutations()


profile_question_schema = graphene.Schema(query=ProfileQuestionQuery, mutation=ProfileQuestionMutator)

