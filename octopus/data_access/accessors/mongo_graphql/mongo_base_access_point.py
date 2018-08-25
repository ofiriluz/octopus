import graphene

# Every access point will Meta inherit this
class AccessPoint(graphene.Interface):
    query_id = graphene.ID()
    access_point_name = graphene.String()
    access_point_data_timestamp = graphene.DateTime()
    access_point_path = graphene.String()
