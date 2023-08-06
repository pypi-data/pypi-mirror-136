
# # WSGI 是同步版的服务器，就目前来说没有什么理由使用同步版的。所以干脆直接去掉。
# # WSGI_APPLICATION = 'mainapp.wsgi.application'
# # 异步版的用起来，就算是开发环境中运行，都感觉一模一样。

# import os

# from django.core.wsgi import get_wsgi_application
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainapp.settings')

# application = get_wsgi_application()
