import graphene
from octopus.data_access.types.common import ProfileAccessPoint

class ProfileHintType(graphene.Enum):
    REGEX = 1
    HAMMING = 2

class ProfileQueryHints(graphene.ObjectType):
    hint_string = graphene.String()
    hint_type = graphene.Field(type=ProfileHintType)

class ProfileQuery(graphene.ObjectType):
    query = graphene.String()
    query_hints = graphene.Field(type=ProfileQueryHints)
    query_host = graphene.String()
    search_time = graphene.DateTime()
    access_points = graphene.List(of_type=ProfileAccessPoint)
    profiler_results = graphene.List(of_type=graphene.ID)
