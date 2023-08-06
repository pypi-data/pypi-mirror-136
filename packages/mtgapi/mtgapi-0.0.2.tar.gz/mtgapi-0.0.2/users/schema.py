from datetime import datetime
# from turtle import title
import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from . import models

class UserType(DjangoObjectType):
    class Meta:
        model = models.User
        fields = ('email', 'name','picture','gender','nickname','created_at')
        # 或者所有字段
        # fields = "__all__"

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)

    def resolve_me(root, info):
        try:
            return models.User.objects.get(pk=info.context.user.id)
        except models.User.DoesNotExist:
            return None
 

