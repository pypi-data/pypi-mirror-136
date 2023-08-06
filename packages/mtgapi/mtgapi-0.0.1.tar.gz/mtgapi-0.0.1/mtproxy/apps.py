import sys
import os
from django.apps import AppConfig


##
## 说明： django 3.2 版，会自动识别AppConfig类，并执行。
## 
class MtproxyConfig(AppConfig):

    default_auto_field = 'django.db.models.BigAutoField' #这个字段不知道具体怎么发挥作用，室抄的。
    name = 'mtproxy'
    verbose_name = "端口转发管理"
    def ready(self):
        # 在开发环境中实际上是执行两次，因为其中一次是 server reloader 功能另外启动的一个进程。
        # python manage.py runserver --noreload
        # 在生产环境中使用的是uwsgi 只启动一次（没实测）
 
        # if 'runserver' not in sys.argv:
        #     return True
        if 'dumpdata' in sys.argv:
            return True
        print("====mtproxy 模块启动=====", flush=True)

        # you must import your modules here 
        # to avoid AppRegistryNotReady exception 
        # from .models import MyModel 
        # startup code here

        # 或者根据明确的环境变量，
        # if os.environ.get('RUN_MAIN'):
        #     print("STARTUP AND EXECUTE HERE ONCE.")
        from . import signals
        


 


 