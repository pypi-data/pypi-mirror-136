from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver # 导入receiver监听信号
from django.db.models.signals import post_save # 导入post_save信号
from shortuuidfield import ShortUUIDField
from django.contrib.auth import get_user_model
"""
更多的自定义用户管理方式，可参考文章：https://docs.djangoproject.com/zh-hans/3.2/topics/auth/customizing/
"""
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        根据邮箱和密码创建创建普通用户
        """
        if not email:
            raise ValueError('Users must have an email address')        
        user = self.model(
            email=self.normalize_email(email),
        )
    
        user.set_password(password) #自动使用django默认的方式加密了密码。
        user.save(using=self._db)
        return user
 
    def create_superuser(self, email, password):
        """
        根据邮箱和密码创建超级用户
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """自定义系统用户模型"""
    objects = UserManager()
    username = None 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    name = models.CharField(max_length=50, default='Anonymous')
    email = models.EmailField(max_length=100, unique=True)
    session_token = models.CharField(max_length=10, default=0) 
    active = models.BooleanField(default=True)
    # a admin user; non super-user
    is_superuser = models.BooleanField(default=False) # a superuser 
    is_active = models.BooleanField(default=True,verbose_name="激活状态")
    is_staff = models.BooleanField(default=False,verbose_name="是否是员工")
    created_at = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    ## 可以继续添加更多的自定义字段。
    GENDER_TYPE = (
        ("1","男"),
        ("2","女")
    )
    picture = models.ImageField(upload_to="Store/user_picture",verbose_name="用户头像",null=True,blank=True)
    phone = models.CharField(max_length=11,null=True,blank=True,verbose_name="手机号码")
    gender = models.CharField(max_length=2,choices=GENDER_TYPE,verbose_name="性别",null=True,blank=True)
    home_address = models.CharField(max_length=100,null=True,blank=True,verbose_name="地址")
    nickname = models.CharField(max_length=13,verbose_name="昵称",null=True,blank=True)

    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = '系统用户'
        verbose_name_plural = verbose_name

#
class Address(models.Model):
    """
    收货地址，通过定义模型来添加权限（演示）
    """
    recv_address = models.TextField(verbose_name = "收货地址")
    receiver =  models.CharField(max_length=32,verbose_name="接收人")
    recv_phone = models.CharField(max_length=32,verbose_name="收件人电话")
    post_number = models.CharField(max_length=32,verbose_name="邮编")
    buyer_id = models.ForeignKey(to=settings.AUTH_USER_MODEL,on_delete = models.CASCADE,verbose_name = "用户id")
    class Meta:
        permissions = (
            ("view_addresses", "查看地址"),
        )
# 通过代码添加权限(演示)
# from django.contrib.auth.models import Permission,ContentType
# from .models import Address
# content_type = ContentType.objects.get_for_model(Address)
# permission = Permission.objects.create(name = "查看地址",codename = "view_addresses",content_type = content_type)

# User模型和权限之间可以通过以下几种方式来进行管理：
# 1、user.user_permissions.set(permission_list)：直接给定一个权限的列表。
# 2、user.user_permissions.add(permission,permission,...)：一个个添加权限。
# 3、user.user_permissions.remover(permission,permission)：一个个删除权限。
# 4、user.user_permissions.clear()：清除权限
# 5、user.has_perm('<app_name>.<codename>')：判断是否拥有某个权限，权限参数是一个字符串，格式是app_name.codename。
# 6、user.get_all_permission()：获得所有权限。
