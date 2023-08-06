import os
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack 
import django.urls


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainapp.settings')
import django
django.setup()


##
## 由于MyGraphqlWsConsumer导入时实际上触发了很多其他模块的导入，例如某些model。
## 这需要django核心修复才不搞错。  那么在生产环境中，实用daphne，跟直接用，manage.py runserver 有差异
## 导致报错，解决方式是，先执行：django.setup()。
##
from .consumers import MyGraphqlWsConsumer
# 下面这句是默认的。
# application = get_asgi_application()

# # 添加channels的支持
application = ProtocolTypeRouter({
    "http": get_asgi_application(), 
    "websocket": URLRouter([
        django.urls.path("graphql/", MyGraphqlWsConsumer.as_asgi()),
    ])
})