import graphene
import graphql_jwt
import ingredients.schema
import mtproxy.schema
import mtx.schema
import users.schema
import vpngate.schema
from graphene_django.debug import DjangoDebug
from .subscription import OnNewChatMessage
from rx import Observable
import asyncio
import datetime


class Query(
    users.schema.Query,
    ingredients.schema.Query, 
    mtx.schema.Query, 
    mtproxy.schema.Query,
    vpngate.schema.Query,
    graphene.ObjectType):
    """提示： 通过这个方式，引入各个子项目的graphql scheme"""
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    debug = graphene.Field(DjangoDebug, name='_debug') # graphene 调试中间件用到。
 

class DemoSendChatMessageMutation(graphene.Mutation):
    """发送聊天消息的Mutation"""
    class Arguments:
        chatroom = graphene.String(required=True)
        text = graphene.String(required=True)
        sender = graphene.String(required=True) 
    result = graphene.String()
    @classmethod
    def mutate(cls, root, info, chatroom,sender,text):
        OnNewChatMessage.new_chat_message(chatroom,text,sender)
        return DemoSendChatMessageMutation(result="ok")


class Mutation(
    mtx.schema.Mutation, # Add your Mutation objects here
    mtproxy.schema.Mutation,
    graphene.ObjectType
):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    demo_send_chatMessage =  DemoSendChatMessageMutation.Field()


class Subscription(graphene.ObjectType):
    """GraphQL subscriptions."""
    on_new_chat_message = OnNewChatMessage.Field()
 
    hello = graphene.String()

    def resolve_hello(root, info):
        # 每三秒发送一个数据
        return Observable.interval(3000).map(lambda i: "hello -- " + str(datetime.datetime.now()))

    time_of_day = graphene.String()

    async def subscribe_time_of_day(root, info):
        while True:
            yield datetime.now().isoformat()
            await asyncio.sleep(1)

# 总schema
schema = graphene.Schema(query=Query, mutation=Mutation, subscription=Subscription)








