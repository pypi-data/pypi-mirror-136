from datetime import datetime
# from turtle import title
import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import MtxDemo, Post
from . import models

class MtxDemoType(DjangoObjectType):
    class Meta:
        model = MtxDemo
        fields = ("id", "name","age") 
        # 或者所有字段
        # fields = "__all__"
        # 额外字段（不在模型中的字段）
        extra_field = graphene.String()
        # 处理额外字段的函数，可以根据实际情况返回一些数据。哪怕是请求其他服务器的数据也行，很灵活。

        def resolve_extra_field(self, info):
            return "hello!"



class MtxDemoNode(DjangoObjectType):
    class Meta:
        model = MtxDemo
        # 这里定义过滤器，亦即前端graphql查询参数。
        # 具体的过滤语法，估计跟django_filter组件有关。
        # 
        filter_fields = {
            'id': ['exact'],
            'name': ['exact', 'icontains', 'istartswith'],
            # 'notes': ['exact', 'icontains'],
            # 'category': ['exact'],
            # 'category__name': ['exact'],
        } 
        interfaces = (relay.Node, )



class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = ('title', 'content')
        # 或者所有字段
        # fields = "__all__"


class PostNode(DjangoObjectType):
    class Meta:
        model = Post
        fields = ('title', 'content')
        interfaces = (relay.Node, )
        filter_fields = {
            'id': ['exact'],
            'title': ['exact', 'icontains', 'istartswith'],
        }
    @classmethod
    def get_queryset(cls, queryset, info):
        """根据权限过滤掉结果集"""
        if info.context.user.is_anonymous:
            print("当前为匿名用户")
            return queryset.filter(published=True)            
        return queryset

    @classmethod
    def get_node(cls, info, id):
        """当查询单个node时，根据权限判断是否返回数据"""
        print("PostNode get_node called")
        try:
            post = cls._meta.model.objects.get(id=id)
        except cls._meta.model.DoesNotExist:
            return None

        if post.published or info.context.user == post.owner:
            return post
        return None


class Query(graphene.ObjectType):
    ##
    ## 学习笔记：普通方式下，有字段名，且有对应的resolve_函数，就能在resolve函数中处理返回的数据对象。
    ## 这是比较原始的方式。
    all_mtxdemos = graphene.List(MtxDemoType)
    def resolve_mtxdemo_by_name(root, info, name):
        try:
            return MtxDemo.objects.filter(name=name).first()
        except MtxDemo.DoesNotExist:
            return None

    mtxdemo_by_name = graphene.Field(MtxDemoType, name=graphene.String(required=True))
    def resolve_all_mtxdemos(root,info):
        print(info) 
        return MtxDemo.objects.all()


    ##
    ## 如果是使用relay的方式，就不用定义resolve 函数，但要预先定义Node类型。
    ##
    all_mtxdemos_relay = DjangoFilterConnectionField(MtxDemoNode)
    mtxdemo = relay.Node.Field(MtxDemoNode)

    ##
    ## 根据不同的权限过滤不同的字段。（也就是说不同权限的用户看到不一样的字段）
    ##
    all_posts = DjangoFilterConnectionField(PostNode)





class MtxDemoMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        text = graphene.String(required=True)
        id = graphene.ID()

    # The class attributes define the response of the mutation
    question = graphene.Field(MtxDemoType)

    @classmethod
    def mutate(cls, root, info, text, id):
        demoItem = MtxDemo.objects.get(pk=id)
        demoItem.name = text
        demoItem.save()
        # Notice we return an instance of this mutation
        return MtxDemoMutation(question=demoItem)

class DemoPostInsertMutation(graphene.Mutation):
    """一次插入100条数据记录，方便测试"""
    # class Arguments:
    #     # The input arguments for this mutation
    #     text = graphene.String(required=True)
    #     id = graphene.ID()
    # # The class attributes define the response of the mutation
    result = graphene.Field(PostType)
    @classmethod
    def mutate(cls, root, info):
        for x in range(0,10):
            newPost = models.Post(title="new post " + str(datetime.now()), owner=info.context.user)     
            newPost.save() 
        return DemoPostInsertMutation(result=newPost)

class Mutation(graphene.ObjectType):
    update_mtx_demo = MtxDemoMutation.Field()
    demo_post_batch_insert = DemoPostInsertMutation.Field()
 



