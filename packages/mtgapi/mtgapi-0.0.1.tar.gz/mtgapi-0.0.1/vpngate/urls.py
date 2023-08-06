from os import name
# from vpngate.vpngate import connect_random
from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'vpnitem', views.VpnItemViewSet,basename="Vpnitem")
router.register(r'vpnconnect', views.VpnConnectViewSet)
# router.register(r'album', views.AlbumViewSet)
# router.register(r'track', views.TrackViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
     # path('',views.index),
     # path('api/', include(router.urls)),
     # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
     # path('fetch/', views.vpnlistfetch, name="fetch_vpn_list"),
     # path('connect/<int:id>/wait', views.connect,
     # {'wait': True}, name="connect_wait",),
     # path("connect_random",views.connect_random),
     # path('connect/<int:id>', views.connect,
     # {'wait': False}, name="connect_nowait",),
     # path('disconnect/<int:vpnitem_id>', views.disconnect),
     # path('openvpnlog/<int:vpnitem_id>', views.openvpnlog, name="openvpnlog"),
     # path('resetenv', views.resetEnv, name="resetenv"),
     # path('sysinfo', views.sysinfo, name="sysinfo"),
     path("tasks_worker_script/", view=views.tasks_worker_script, name="tasks_worker_script")
]