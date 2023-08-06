
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from mainapp.schema import schema
from .views import PrivateGraphQLView
# from .oauth_graphql_view import OAuth2ProtectedGraph
urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('mtx/', include('mtx.urls')),
    path('mtproxy/', include('mtproxy.urls')),
    path('chat/', include('chat.urls')),
    path('vpngate/', include("vpngate.urls")),
    path('api-auth/', include('rest_framework.urls')),

    # django-oauth-toolkit
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),   
    
    # django-simple-captcha 图形验证码
    path('captcha/', include('captcha.urls')),
    # 不需要登陆的graphql视图
    path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))), 
    # 需要登陆的graphql视图
    # path('graphql', csrf_exempt(PrivateGraphQLView.as_view(graphiql=True, schema=schema))),

    # （无用了）需要登陆的graphql视图（由oauth提供认证）
    # path('graphql/', csrf_exempt(OAuth2ProtectedGraph.as_view(graphiql=True, schema=schema))),

    path('__debug__/', include('debug_toolbar.urls')),
] 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
