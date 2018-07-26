from .mongo_base_access_point import AccessPoint
import graphene

class GithubMongoAccessor(graphene.ObjectType):
    class Meta:
        interfaces = (AccessPoint, )

    # TODO
    