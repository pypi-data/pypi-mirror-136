import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from . import models 


class VpnItemNode(DjangoObjectType):
    class Meta:
        model = models.VpnItem
        # 这里定义过滤器，亦即前端graphql查询参数。
        # 具体的过滤语法，估计跟django_filter组件有关。
        # 
        filter_fields = {
            'hostname': ['exact', 'icontains', 'istartswith'],
            # 'notes': ['exact', 'icontains'],
            # 'category': ['exact'],
            # 'category__name': ['exact'],
        } 
        interfaces = (relay.Node, ) 
    primary_text = graphene.String(description='主显示文字')
    def resolve_primary_text(self, info):
        return f"{self}"
 
 


class Query(graphene.ObjectType):
    all_vpn_item = DjangoFilterConnectionField(VpnItemNode)


# class VpngateMutation(graphene.Mutation):
#     pass
    # class Arguments:
    #     # The input arguments for this mutation
    #     text = graphene.String(required=True)
    #     id = graphene.ID()

    # # The class attributes define the response of the mutation
    # portForwardData = graphene.Field(PortForwardType)
    # @classmethod
    # def mutate(cls, root, info, lhost, id):
    #     item = models.PortForward.objects.get(pk=id)
    #     item.lhost = lhost
    #     item.save()
    #     # Notice we return an instance of this mutation
    #     return PortForwardMutation(question=portForwardData)

# class Mutation(graphene.ObjectType):
#     update_mtx_demo = VpngateMutation.Field() 
 



