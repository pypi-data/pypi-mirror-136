from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.core.signals import request_finished
from .models import PortForward

@receiver(pre_save, sender=PortForward)
def my_handler(sender, **kwargs):
    """[summary]
        通过这样方式，能够捕获到数据库记录的变更。
        TODO: 将数据库的变更记录通过graphql subscription 的方式推送到客户端。
    """
    instance = kwargs.get("instance");
    print(f"新记录：{instance}", flush=True)
    print(kwargs)

# @receiver(request_finished)
# def my_callback(sender, **kwargs):
#     pass
#     print("Request finished! ===========")