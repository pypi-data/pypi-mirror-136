

##
## 模块：https://github.com/jaydenwindle/graphene-subscriptions 要求的。
##      原理是：通过django 模型操作的各种信号，最终通过websocket 的方式通知客户端。
##      目前没启用。
##




# # your_app/signals.py
# from django.db.models.signals import post_save, post_delete
# from graphene_subscriptions.signals import post_save_subscription, post_delete_subscription

# from your_app.models import YourModel

# post_save.connect(post_save_subscription, sender=YourModel, dispatch_uid="your_model_post_save")
# post_delete.connect(post_delete_subscription, sender=YourModel, dispatch_uid="your_model_post_delete")

# # your_app/apps.py
# from django.apps import AppConfig

# class YourAppConfig(AppConfig):
#     name = 'your_app'

#     def ready(self):
#         import your_app.signals