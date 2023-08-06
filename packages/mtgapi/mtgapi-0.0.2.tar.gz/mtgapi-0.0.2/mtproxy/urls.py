from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # path('test2/', views.test2),
    path('vpn/connect', views.vpnconnect, name='vpnconnect'),

    ## curl http://csrep.top:8000/mtproxy/onionsshbot/up | bash -
    path('onionsshbot/up', views.onion_ssh_bot_up, name='onionsshbot_up'),
    path("script/",views.script_content,name="script_content"),
    path("git_run/", views.git_run, name="git_run"),
]