import csv
from os import system
import os
from django.db import models
import requests
import subprocess 
import sys
import time
import socket               # 导入 socket 模块
import urllib3
from clint.textui import progress
import base64
import re
from random import Random
from pathlib import Path
from vpngate import utils
from . import models
import shutil
import random
from datetime import datetime
from io import StringIO

from vpngate.vpngatesession import VpngateSession
from vpngate import  network_setting
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)
from . utils2 import Utils
####
cr = None
MISSING = object()
nicely_formatted_csv_data_pattern = "{:<20} {:<20} {:<10} {:<10} {:<10} {:<40} {:<10}"

# 进程列表
openvpn_process = []

openvpnlogdir = "/tmp/mtopenvpn"

DEFULT_VPNLIST_URL = "http://www.vpngate.net/api/iphone/"


def download_vpn_list_content():
    """从服务器下载vpn配置列表"""
    response = requests.get(DEFULT_VPNLIST_URL)
    return response.content.decode()
     
def fetch_and_migrate_vpn_list():
    """从默认网址下载vpngate的公开vpn列表"""
    # response = requests.get(DEFULT_VPNLIST_URL)
    rowcontent = download_vpn_list_content()
    csvlines = list(csv.reader(StringIO(rowcontent), delimiter=','))    
    newCount = savevpnlist(csvlines[2:])  
    #抓取数量
    return (len(csvlines) -2 , newCount)# （下载数，新增数）

def savevpnlist(ovpnlist):
    """写入数据库"""     
    lines = []
    count=0 #新记录数量
    for row in ovpnlist:
        if row[0] == '*':
            break
        else:
            hostname = row[0]
            ip = row[1]
            score = row[2]
            ping = row[3]
            speed = row[4]
            country_long = row[5]
            country_short = row[6]
            num_vpn_sessions = row[7]
            uptime = row[8]
            total_users = row[9]
            total_traffic = row[10]
            logtype = row[11]
            operator = row[12]
            message = row[13]
            openvpn_configdata_base64 = row[14]            
            # 存入数据库   
            logger.debug("抓取到的IP{}".format(ip))
            items = VpnItem.objects.filter(ip= ip)
            #注意不应该大于一个。ip本来打算做主键的，但是旧代码看起来不好改，先不管主键问题。
            if items.count() > 0:
                item = items[0]
                item.hostname = hostname
                item.score = score
                item.ping=ping
                item.speed=speed,
                item.country_long=country_long
                item.country_short=country_short
                item.num_vpn_sessions=num_vpn_sessions
                item.uptime=uptime
                item.total_users=total_users
                item.total_traffic=total_traffic
                item.logtype=logtype
                item.operator=operator
                item.message=message
                item.ovpn_config_text=base64.decodebytes(
                    openvpn_configdata_base64.encode("utf-8")).decode()
            else:
                item = VpnItem(hostname=hostname, ip=ip, score=score,
                                    ping=ping,
                                    speed=speed,
                                    country_long=country_long,
                                    country_short=country_short,
                                    num_vpn_sessions=num_vpn_sessions,
                                    uptime=uptime,
                                    total_users=total_users,
                                    total_traffic=total_traffic,
                                    logtype=logtype,
                                    operator=operator,
                                    message=message,
                                    ovpn_config_text=base64.decodebytes(
                                        openvpn_configdata_base64.encode("utf-8")).decode()
                                    )
                count = count+1
            item.save()
            saveConfigDetail(item)
    return count

def saveConfigDetail(vpnitem):
    """分析ovpn文件，提取更多信息，并保存到数据库"""
    ovpn_content = vpnitem.ovpn_config_text
    def getvolum(name):
        text = re.sub("\r","",ovpn_content)
        r = r"^[^#;]"+name+" (.*)"
        match = re.search(r, text, re.MULTILINE)
        if match:
            logger.debug("[DEBUG]ovpn配置 {}: {}".format(name,match.groups()[0]))
            return match.groups()[0]
    
    ovpnConfig = models.VpnOvpn()
    ovpnConfig.proto = getvolum("proto")    
    ovpnConfig.host, ovpnConfig.port = getvolum("remote") .split(' ')
    ovpnConfig.save()

    vpnitem.ovpnconfig = ovpnConfig
    vpnitem.save()

def check_vpn_avariable(vpnitem):
    """检查一个vpn是否能够连接"""
    conn = VpngateSession(vpnitem).connect().wait()
    if conn.isProcesslive():
        logger.debug("已经连接上，通道名：{}, 进程PID：{}".format(conn.tunName, conn.getPid()))
        return True
    else:
        logger.debug("vpnitem {} 尝试连接失败".format(vpnitem.ip))
        return False

def connect_random():
    defaultDevIP = network_setting.getDefaultDevIp()
    vpnitems = models.VpnItem.objects.all()
    print("总共有{}个对象".format(vpnitems.count()))
    # shuffle 打乱
    numberList = [ x for x in range(0,vpnitems.count())]
    random.shuffle(numberList)        
    for num in numberList:
        item = vpnitems[num]
        print("开始检测id:{}, ip:{}".format(item.id,item.ip))
        conn = VpngateSession(item)
        conn.connect().wait()
        isUp = conn.isOk
        # isUp  = vpngate.check_vpn_avariable(item)
        status = models.VpnStatus()
        status.isUp = isUp 
        status.save()
        item.status = status
        item.save()
        if isUp:
            print("连接成功id:{}, ip:{}".format(item.id,item.ip))
            status.last_up_at = timezone.now()

            print("开始通知vpnserver设置网关")
            port = os.environ.get("OVPN_SERVER_GATEWAYAPI_SERVICE_PORT")
            host = os.environ.get("OVPN_SERVER_GATEWAYAPI_SERVICE_HOST")
            url = "http://{}:{}/setgateway/{}".format(host,port,defaultDevIP)
            response = requests.get(url)
            print("响应:{}".format(response.content.decode()))               
            break
        else:
            status.last_check_at = timezone.now()
            print("连接失败:{}".format(isUp))
    
class VPNGateApp:
    """准备丢弃"""
    def __init__(self, URL="http://www.vpngate.net/api/iphone/"):
        self.URL = URL
        self._cache_file_path = ".cache/vpndata.csv"
        self.ovpnlist = self.get_ovpn_list_cache()
        if not self.ovpnlist:
            self.grab_csv()
        return

    def write_openvpn_file(self, b64ovpndata, vpnname):
        """takes a base64 string and saves it out as an .ovpn file"""
        openvpnconfigpath = ".vpnconfigs/vpnconfig_{0}.ovpn".format(vpnname)
        decoded_ovpndata = base64.decodebytes(
            b64ovpndata.encode(encoding="utf-8"))

        Utils.create_directory_path(openvpnconfigpath)
        fh = open(openvpnconfigpath, "wb")
        fh.write(decoded_ovpndata)
        fh.write(
            b'\nscript-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf')
        fh.close()

        # print decoded_ovpndata
        return self.grab_ovpn_values(openvpnconfigpath)

    def grab_ovpn_values(self, openvpnconfigpath):

        protocol = None
        address_and_port = None
        address = None
        port = None

        for line in open(openvpnconfigpath, 'r'):
            # print(line)
            if protocol == None:
                # pattern = re.compile("^proto (tcp|udp)\r$") #tcp or udp?
                match = re.match('^proto (tcp|udp)', line)

                if match:
                    print("found: " + match.group(1))
                    protocol = match.group(1)
                else:
                    pass

            if address_and_port == None:
                # ip address and port
                pattern2 = re.compile("^remote ([0-9\.]*) ([0-9]*)$")
                match2 = pattern2.match(line)

                if match2:
                    print("found: " + match2.group(1) + " " + match2.group(2))
                    address_and_port = match2
                    address = match2.group(1)
                    port = match2.group(2)
                else:
                    pass

        return protocol, address, port

    

    def grab_csv(self):
        """grabs the csv from the vpngate website"""

        print(
            "grabbing VPNGate CSV from : {0}, this may take a minute...".format(self.URL))
        print("ctrl+c if you already have a cached list")

        with requests.Session() as session:
            r = session.get(self.URL, stream=True, hooks=dict(
                response=self.grab_csv_callback))

            # it seems that the requests module had a bug, or didn't support content-length headers /
            # in the response, so here we use urllib2 to do a HEAD request prior to download

            http = urllib3.poolmanager.PoolManager()
            # request2 = http.request('GET',self.URL)
            # request2.get_method = lambda : 'HEAD'
            # urllib3.urlopen(request2)
            response2 = http.request('GET', self.URL)
            total_length = int(response2.info()['Content-Length'])

            Utils.create_directory_path(self._cache_file_path)
            with open(self._cache_file_path, 'wb') as f:
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()

        return

    def grab_csv_callback(self, r, *args, **kwargs):
        print("data returned from {url}".format(url=r.url))

        return

    def grab_vpndata(self, chosenVPNName):
        file_handle.seek(0)
        for utf8_row in cr:
            if(chosenVPNName == utf8_row[0]):
                return utf8_row[14]
        return None

    def parse_csv(self, chosenCountryShortCodeArg=MISSING):
        global cr, MISSING, file_handle
        file_handle = open(self._cache_file_path, "r")
        cr = csv.reader(file_handle, delimiter=',')

        # for utf8_row in cr:
        #     (a) = utf8_row[:-1]
        #     if len(a) != 0:
        #         if chosenCountryShortCodeArg is MISSING:
        #              print(nicely_formatted_csv_data_pattern.format(*a))
        #         else:
        #             if a[6] == chosenCountryShortCodeArg:
        #                 print(nicely_formatted_csv_data_pattern.format(*a))
        return

    def get_ovpn_list_cache(self, cache=True):
        """获取vpn列表"""

        ret = None
        if cache:
            cache_file = Path(self._cache_file_path)
            if cache_file.exists():
                ret = [row for row in csv.reader(
                    open(self._cache_file_path, "r"), delimiter=',')]

        if not ret:
            self.grab_csv()

        ret = [row for row in csv.reader(
            open(self._cache_file_path, "r"), delimiter=',')]
        return ret[2::]  # 由于是csv格式，第一行是说明，第二行是表头，可以丢弃。

    def fetch_vpngatecsvlist(self):
        """从默认网址下载vpngate的公开vpn列表"""
        with requests.Session() as session:
            r = session.get(self.URL, stream=True, hooks=dict(
                response=self.grab_csv_callback))
            http = urllib3.poolmanager.PoolManager()
            response2 = http.request('GET', self.URL)
            total_length = int(response2.info()['Content-Length'])
            Utils.create_directory_path(self._cache_file_path)
            with open(self._cache_file_path, 'wb') as f:
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()

            self.importVpnitemCsv2DB()
        
    def importVpnitemCsv2DB(self):
        # 读取
        self.ovpnlist = [row for row in csv.reader(
            open(self._cache_file_path, "r"), delimiter=',')]
        # 入库
        list2 = self.ovpnlist[2::]
        self.savevpnlist(list2)

    def savevpnlist(self, ovpnlist):
        # csvrows = vpnapp.get_ovpn_list_cache()
        lines = []
        for row in ovpnlist:
            # HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,Uptime,
            # TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64
            if row[0] != '*':
                hostname = row[0]
                ip = row[1]
                score = row[2]
                ping = row[3]
                speed = row[4]
                country_long = row[5]
                country_short = row[6]
                num_vpn_sessions = row[7]
                uptime = row[8]
                total_users = row[9]
                total_traffic = row[10]
                logtype = row[11]
                operator = row[12]
                message = row[13]
                openvpn_configdata_base64 = row[14]
                # lines.append("{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}".format(name, ip, a2, a3, a4, a5, a6))
                # 存入数据库
                db_row = models.VpnItem(hostname=hostname, ip=ip, score=score,
                                 ping=ping,
                                 speed=speed,
                                 country_long=country_long,
                                 country_short=country_short,
                                 num_vpn_sessions=num_vpn_sessions,
                                 uptime=uptime,
                                 total_users=total_users,
                                 total_traffic=total_traffic,
                                 logtype=logtype,
                                 operator=operator,
                                 message=message,
                                 # openvpn_configdata_base64  =openvpn_configdata_base64
                                 ovpn_config_text=base64.decodebytes(
                                     openvpn_configdata_base64.encode("utf-8")).decode()
                                 )
                db_row.save()

    def check_avriable(self, vpnitem):
        """检测是否能够连接"""
        vpns = self.get_ovpn_list_cache()
        for vpn in vpns:
            print("开始检测：{}".format(vpn))
            # 尝试端口连接
            # TODO：UDP方式连接的也要处理
            s = socket.socket()         # 创建 socket 对象
            host = socket.gethostname()  # 获取本地主机名
            port = 12345                # 设置端口号
            s.connect((host, port))
            s.close()