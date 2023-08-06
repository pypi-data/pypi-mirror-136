from xmlrpc.client import DateTime
import datetime
import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from . import models 

class PortForwardType(DjangoObjectType):
    """这个类暂时没用上。先屏蔽掉。"""
    class Meta:
        model = models.PortForward
        # fields = ("id", "name","age") 
        # 或者所有字段
        fields = "__all__"
        # 额外字段（不在模型中的字段）
        extra_field = graphene.String()
        primary_text = graphene.String()
        # 处理额外字段的函数，可以根据实际情况返回一些数据。哪怕是请求其他服务器的数据也行，很灵活。
        def resolve_extra_field(self, info):
            return "hello!"
        def resolve_primary_text(self, info):
            return "hello!" + info



class PortForwardNode(DjangoObjectType):
    class Meta:
        model = models.PortForward
        # 这里定义过滤器，亦即前端graphql查询参数。
        # 具体的过滤语法，估计跟django_filter组件有关。
        # 
        filter_fields = {
            'lhost': ['exact', 'icontains', 'istartswith'],
            # 'notes': ['exact', 'icontains'],
            # 'category': ['exact'],
            # 'category__name': ['exact'],
        } 
        interfaces = (relay.Node, ) 
    primary_text = graphene.String(description='主显示文字')
    def resolve_primary_text(self, info):
        return f"{self}" #self.lhost

class OvpnNode(DjangoObjectType):
    class Meta:
        model = models.Ovpn
        # 这里定义过滤器，亦即前端graphql查询参数。
        # 具体的过滤语法，估计跟django_filter组件有关。
        # 
        filter_fields = {
            'host': ['exact', 'icontains', 'istartswith'],
            # 'notes': ['exact', 'icontains'],
            # 'category': ['exact'],
            # 'category__name': ['exact'],
        } 
        interfaces = (relay.Node, ) 
    primary_text = graphene.String(description='主显示文字')
    def resolve_primary_text(self, info):
        return f"{self}"
 

class BotNode(DjangoObjectType):
    class Meta:
        model = models.Bot
        # 这里定义过滤器，亦即前端graphql查询参数。
        # 具体的过滤语法，估计跟django_filter组件有关。
        # 
        filter_fields = {
            'host': ['exact', 'icontains', 'istartswith'],
            # 'notes': ['exact', 'icontains'],
            # 'category': ['exact'],
            # 'category__name': ['exact'],
        } 
        interfaces = (relay.Node, ) 

    pk = graphene.Int()
    primary_text = graphene.String(description='主显示文字')
    def resolve_primary_text(self, info):
        return f"{self}"
    def resolve_pk(self, info):
        return self.pk

 

class BotLogNode(DjangoObjectType):
    class Meta:
        model = models.BotLog
        # 这里定义过滤器，亦即前端graphql查询参数。
        # 具体的过滤语法，估计跟django_filter组件有关。
        # 
        filter_fields = {
            'id': ['exact', 'icontains', 'istartswith'],
            # 'notes': ['exact', 'icontains'],
            # 'category': ['exact'],
            # 'category__name': ['exact'],
        } 
        interfaces = (relay.Node, ) 
    pk = graphene.Int()
    def resolve_pk(self, info):
        return self.pk
    primary_text = graphene.String(description='主显示文字')
    def resolve_primary_text(self, info):
        return f"{self}"

 



class Query(graphene.ObjectType):
    ##
    ## 学习笔记：普通方式下，有字段名，且有对应的resolve_函数，就能在resolve函数中处理返回的数据对象。
    ## 这是比较原始的方式。
    # all_port_forwards = graphene.List(MtxDemoType)
    # def resolve_mtxdemo_by_name(root, info, name):
    #     try:
    #         return MtxDemo.objects.filter(name=name).first()
    #     except MtxDemo.DoesNotExist:
    #         return None

    # mtxdemo_by_name = graphene.Field(MtxDemoType, name=graphene.String(required=True))
    # def resolve_all_mtxdemos(root,info):
    #     print(info) 
    #     return MtxDemo.objects.all()


    ##
    ## 如果是使用relay的方式，就不用定义resolve 函数，但要预先定义Node类型。
    ##
    all_port_forwards_relay = DjangoFilterConnectionField(PortForwardNode)    
    port_forward = relay.Node.Field(PortForwardNode)
    all_ovpn = DjangoFilterConnectionField(OvpnNode)
    all_bot = DjangoFilterConnectionField(BotNode)
    all_bot_log = DjangoFilterConnectionField(BotLogNode)






class PortForwardMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        text = graphene.String(required=True)
        id = graphene.ID()

    # The class attributes define the response of the mutation
    portForwardData = graphene.Field(PortForwardType)
    @classmethod
    def mutate(cls, root, info, lhost, id):
        item = models.PortForward.objects.get(pk=id)
        item.lhost = lhost
        item.save()
        # Notice we return an instance of this mutation
        return PortForwardMutation(question=portForwardData)

# 普通方式的muation
# class BotLogMutation(graphene.Mutation):
#     class Arguments:
#         # The input arguments for this mutation
#         content = graphene.String(required=True)        
#         botId = graphene.ID()

#     # The class attributes define the response of the mutation
#     result = graphene.Field(graphene.String)
#     @classmethod
#     def mutate(cls, root, info, content, botId):
#         item = models.BotLog()
#         item.content = content
#         item.bot = models.Bot.objects.get(pk=botId)
#         item.save()
#         # Notice we return an instance of this mutation
#         return BotLogMutation(result=0)

class BotLogMutation(relay.ClientIDMutation):
    """注意，这个实用relay版本的mutation"""
    class Input:
        content = graphene.String(required=True)
        bot_id = graphene.ID(required=True)

    # ship = graphene.Field(Ship)
    # faction = graphene.Field(Faction)
    result = graphene.Field(graphene.String)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):   
        content = input["content"]
        bot_id = input["bot_id"]
        item = models.BotLog()
        item.content = content
        item.bot = models.Bot.objects.get(pk=bot_id)
        item.save()
        # ship = create_ship(ship_name, faction_id)
        # faction = item #//get_faction(faction_id)     
        return BotLogMutation(result="")

class BotMutation(relay.ClientIDMutation):
    """注意，这个实用relay版本的mutation"""
    class Input:
        pk = graphene.Int(required=True)
        is_live = graphene.Boolean(required=True)
        # bot_id = graphene.ID(required=True)

    # ship = graphene.Field(Ship)
    # faction = graphene.Field(Faction)
    result = graphene.Field(graphene.String)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):   
        # content = input["content"]
        # bot_id = input["bot_id"]
        print(input)
        item = models.Bot.objects.get(pk=input["pk"])
        item.is_live = input["is_live"]
        item.updated_at = datetime.datetime.now
        item.save()
        # ship = create_ship(ship_name, faction_id)
        # faction = item #//get_faction(faction_id)     
        return BotMutation(result="")

class Mutation(graphene.ObjectType):
    update_mtx_demo = PortForwardMutation.Field() 
    add_bot_log = BotLogMutation.Field()
    update_bot_status = BotMutation.Field()
 



