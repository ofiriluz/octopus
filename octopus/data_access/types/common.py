import graphene

class ProfileAccessPoint(graphene.ObjectType):
    access_point_name = graphene.String()
    access_point_id = graphene.ID()