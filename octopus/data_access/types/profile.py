import graphene
from octopus.data_access.types.common import ProfileAccessPoint

class Profile(graphene.ObjectType):
    query_id = graphene.ID()
    access_points_used = graphene.List(of_type=ProfileAccessPoint)
    profiling_timestamp = graphene.DateTime()
    profiling_duration = graphene.Time()
    # TODO - Add the rest of the profiling info as we go

schema = graphene.Schema(query=Profile)