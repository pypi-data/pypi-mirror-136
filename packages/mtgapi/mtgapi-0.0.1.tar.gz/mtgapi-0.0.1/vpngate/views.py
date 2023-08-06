from os import system
import os
from django.shortcuts import render
from django.http import HttpResponse
from . import models
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import  VpnItemSerializer, VpnConnectSerializer
import docker
import json
import base64
import vpngate
from rest_framework.decorators import action
from rest_framework.response import Response
import logging
import threading
class VpnItemViewSet(viewsets.ModelViewSet):
    queryset = models.VpnItem.objects.all()
    serializer_class = VpnItemSerializer
    permission_classes = [permissions.AllowAny]

class VpnConnectViewSet(viewsets.ModelViewSet):
    queryset = models.VpnConnect.objects.all()
    serializer_class = VpnConnectSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False)
    def active_connections(self, request):
        objects = models.VpnConnect.objects.filter(status="connected")

        page = self.paginate_queryset(objects)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(objects, many=True)
        return Response(serializer.data)

# def index(request):
#     context = {
#         "vpnitems":models.VpnItem.objects.all()
#         }
#     return render(request,"vpngateapi/index.html",context)

def apiSuccess(data=None):
    return HttpResponse(json.dumps({"result":True, "data":data}))

def vpnlistfetch(request):
    """抓取数据，存入数据库"""
    VPNGateApp().fetch_list()
    
    return HttpResponse("\n".join("方法未实现"))


def connect(request, id, wait):
    """本机调用openvpn连接"""
    vpnitem = models.VpnItem.objects.get(id=id)
    vpnsession = VpngateSession(vpnitem)
    vpnsession.connect()
    if(wait == 1):
        connect_status = vpnsession.wait_connected_or_timeout()
        return  apiSuccess({"connect_status":connect_status})
    else:
        return apiSuccess({"status":"connecting"})

def connect_random(request):
    """随机连接"""
    thread= threading.Thread(target=vpngate.connect_random, daemon=True)
    thread.start()
    return apiSuccess()

# def disconnect(request, vpnitem_id):
#     """断开指定vpnitem的连接"""
#     vpnitem = models.VpnItem.objects.get(id=vpnitem_id)
#     VpnConnectionManager.disConnect(vpnitem)
#     return  HttpResponse(json.dumps({"result":True}))



def connect_info(request, vpnitem_id):
    """连接状态"""
    vpnitem = models.VpnItem.objects.get(id=vpnitem_id)
    connect_info = vpnitem.connect_info

# def openvpnlog(request, vpnitem_id):
#     """获取完整的openvpn进程输出"""
#     vpnitem = models.VpnItem.objects.get(id=vpnitem_id)
#     logtext = VpnConnectionManager.getOpenvpnFullLog(vpnitem)
#     return  apiSuccess({"logtext":logtext})

# def resetEnv(request):
#     VpnConnectionManager.initopenvpnEnv()
#     return  apiSuccess({"result":True})

def sysinfo(request):
    """返回系统关键信息（目前用于查看）"""
    logging.debug("返回系统关键信息（目前用于查看）")
    
    lines = []
    import netifaces
    interfaces = netifaces.interfaces()
    lines.append("网卡列表：")
    lines.append(str(interfaces))
    lines.append("--------------------")
    for i in interfaces:
        lines.append("网卡：{}:".format(i))
        ifaddr = netifaces.ifaddresses(i)
        lines.append(str(ifaddr))
    return  apiSuccess({"data":"\n".join(lines)})

def tasks_worker_script(request):
    base_path = os.path.split(os.path.realpath(__file__))[0]
    print(f"当前路径{base_path}")
    with open(f"{base_path}/tasks.py") as f:
        text = f.read()
        return HttpResponse(text)