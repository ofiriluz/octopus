import graphene
from octopus.data_access.types.common import ProfileAccessPoint
from octopus.data_access.db.db_connection_pool import DBConnectionPool

class Profile(graphene.ObjectType):
    query_id = graphene.ID()
    access_points_used = graphene.List(of_type=ProfileAccessPoint)
    profiling_timestamp = graphene.DateTime()
    profiling_duration = graphene.Time()
    # TODO - Add the rest of the profiling info as we go

class ProfileQuery(graphene.ObjectType):
    profile = graphene.Field(type=Profile)

    def resolve_profile(self, info, id):
        db_pool = DBConnectionPool()
        controller = db_pool.generate_db_controller()
        # TODO

class ProfileMutation(graphene.ObjectType):
    # TODO
    pass

profile_schema = graphene.Schema(query=ProfileQuery, mutation=ProfileMutation)