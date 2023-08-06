import time
import random
import subprocess
import shlex
import netifaces
import sys
import os
import re
import IPy

from vpngate import shell

import logging
logger = logging.getLogger(__name__)
# 默认能连接外网的网卡名。
DEFAULT_DEV = "eth0"
#内网网段
LAN_NET="10.9.9.0/24"
#容器网络
DOCKER_HOST_LAN = "172.17.0.0/24"
WORK_LAN = "10.0.0.0/24"
#默认NAT通道
DEFAULT_NAT_TUNNAL = "tun1000"

def get_gateway_ip_from_routetable():
    """通过查找操作系统的路由表获取默认路由"""
    cmd = "ip route | grep default | awk '{print $3}'"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    p.wait()
    results = p.stdout.readlines()
    if len(results) == 1:
        return results[0].strip()
    return None

def get_gatewayip_from_defaultdev():
    """以网卡IP末尾改为1作为默认网关
    从默认网卡的IP末尾改为1"""    
    ipaddr = getDefaultDevIp()
    ret = re.sub(r"\d{1,3}$", "1", ipaddr)
    return ret

def getDefaultDevIp():
    """获取默认网卡IP"""
    default_dev_if = netifaces.ifaddresses(DEFAULT_DEV)
    # 只处理网卡的第一个IP地址
    ipaddr = default_dev_if[netifaces.AF_INET][0]["addr"]
    return ipaddr


def getDefaultGatewayIp():
    """获取本机路由，优先顺序：环境->默认路由->末尾改为1"""
    a = os.environ.get("GATEWAYIP", None) or get_gateway_ip_from_routetable() or get_gatewayip_from_defaultdev()
    #不知哪个地方返回的是二进制，这里转化一下。懒得找问题。
    if(type(a) == bytes):
        a = a.decode()
    return a

def routeAddWhiteIp(ip):
    """增加白名单IP：在操作系统的路由表中，增加一个主机路由，主机通过“默认路由”连接外网"""
    #先删除旧的（如果有）
    shell.run("sudo route del -host {}".format(ip, getDefaultGatewayIp()))
    #多删除一次也没问题，万一不知道什么原因有多个呢
    shell.run("sudo route del -host {}".format(ip, getDefaultGatewayIp()))
    #添加
    shell.run("sudo route add -host {} gw {}".format(ip, getDefaultGatewayIp()))

def addRoute(net):
    """添加网段路由，参数形如：10.9.9.0/24"""
    lannet = IPy.IP(net)
    ip_zero = lannet[0]#得到末尾0的IP，形如10.9.9.0
    netmask = lannet.netmask()
    # shell.run("sudo route del -net {}".format(lannet))
    shell.run("sudo route add -net {} netmask {} gw {}".format(
        ip_zero,netmask,getDefaultGatewayIp()))

##弃用，因为只需要开机时初始化一次。没有必要重设。
def resetNetworkSetting():
    """初始化本机网络环境"""
    #删除默认路由
    # shell.run("sudo route del default")
    # shell.run("sudo route del -net 0.0.0.0 netmask 0.0.0.0")
    #TODO:可以考虑连NAT也设置
    #清理旧的。
    # shell.run("sudo iptables -t nat -F")
    #添加
    # shell.run("sudo iptables -t nat -A POSTROUTING -s {} -o {} -j MASQUERADE".format(WORK_LAN, DEFAULT_NAT_TUNNAL))
    
    defaultgw = getDefaultGatewayIp()
    logger.debug('识别到的默认网关:{}'.format(defaultgw))

    #添加当前内网路由
    addRoute(LAN_NET)
    addRoute(WORK_LAN)
    # addRoute(DOCKER_HOST_LAN)
    # addRoute("8.8.8.8/32")

def initEnv():
    """对环境进行必要的初始化"""
    p = subprocess.run(shlex.split("""
        if [ ! -d /dev/net ]; then mkdir /dev/net; fi &&
        if [ ! -c /dev/net/tun ]; then mknod /dev/net/tun c 10 200; fi
    """))


