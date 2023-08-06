from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MtxCategory(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name


class MtxDemo(models.Model):
    name = models.CharField(max_length=100)
    ## 关联对象字段（演示）
    category = models.ForeignKey(MtxCategory, on_delete=models.CASCADE)
    age = models.IntegerField(help_text="年龄")
    email = models.CharField(max_length=100, null=True, blank=True, default="a@a.com", help_text="测试邮件")
    some_content = models.CharField(max_length=100, null=True,blank=True, default="null content", help_text="测试内容")


    ##字段过滤器，功能
    filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'age': ['exact', 'icontains'],
            'email': ['exact'],
            'category__name': ['exact'],
        }

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    published = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return self.title
 