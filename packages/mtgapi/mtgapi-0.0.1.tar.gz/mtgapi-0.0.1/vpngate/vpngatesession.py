import os
from signal import signal
import requests
import subprocess
import sys
from clint.textui import progress
from random import Random
from pathlib import Path
# from utils import Utils
from vpngate.models import VpnItem, VpnConnect, VpnStatus
# from mtpylib.shell.shell_helper import excuteCommand
import shutil
import random
from datetime import datetime
import shlex
import time
import threading
import psutil
import re
from django.utils import timezone
from . import network_setting
from vpngate import env
import logging
logger = logging.getLogger(__name__)

#最大重试次数
VPN_CONNECT_RETRY_MAX=1
# 会话，进程map
vpngate_processes = {}
connections = {}


class VpngateSession:
    def __init__(self, vpnitem):
        if vpnitem is None:
            raise Exception("vpn should not none")
        self.vpnitem = vpnitem
        self.tunName=None
        self.pid = None
        self.openvpndatadir = os.path.abspath("openvpndata")
        if not os.path.exists(self.openvpndatadir):
            os.makedirs(self.openvpndatadir)

        self.basedir = "{}/vpnitem-{}".format(self.openvpndatadir,self.vpnitem.id)
        if not os.path.exists(self.basedir):
            os.makedirs(self.basedir)

        #openvpn 自身的日志输出
        self.logfilepath = "{}/openvpn.log".format(self.basedir)
        #ovpn 配置文件
        self.openvpn_configpath = "{}/config.ovpn".format(self.basedir)
        #进程id文件
        self.openvpn_pidpath = "{}/.pid".format(self.basedir)

        #状态文件
        self.openvpn_status_path = "{}/status.txt".format(self.basedir)
        #调试日志文件
        self.debuglogpath = "{}/debug.log".format(self.basedir)
        

        #设置日志输出
        #分开的文件日志
        self.logger = logging.getLogger('vpntread-{}'.format(vpnitem.id))
        self.logger.addHandler(logging.handlers.RotatingFileHandler(self.debuglogpath,"a", 0, 1)  )  
        self.logger.setLevel(logging.DEBUG)

        
        #标准输出日志
        BASIC_FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
        chlr = logging.StreamHandler() # 输出到控制台的handler
        chlr.setFormatter(formatter)         
        self.logger.addHandler(chlr)

        self.parseOvpnConfig()

    def connect(self,tunName="tun1000"):
        # """本机启动openvpn，根据vpnitem信息，进行vpn连接。"""
        self.tunName = tunName
        #由于可能没有默认路由连接外网，所以这里先添加一条主机路由
        # network_setting.routeAddWhiteIp(self.serverHost)
        self.startupOpenvpnDeamon()
        return self

    def disconnect(self):
        """断开vpngate连接"""
        pid = self.getPid()
        if pid > 0:
            complateProcess = subprocess.run(shlex.split("sudo kill {}".format(pid)))
            if complateProcess.returncode != 0:
                self.logger.debug("好像没能杀死进程,pid={}, returncode={}".format(
                    pid, complateProcess.returncode))

        else:
            self.logger.debug("[DEBUG]:找不到进程文件：{}",self.openvpn_pidpath)

        # TODO：可能还需要设置状态，例如self.isOk
        return self

    def wait(self, timeout = 10):
        """等待连接成功或者连接超时"""
        self.isFatalError = False
        self.isAUTH_FAILED_EXITING=False
        while self.isProcesslive():
            self.parseOpenvpnlog()
            if self.isOk:
                self.logger.debug("看起来已经连接上了, vpnitemid={}, pid={}".format(self.vpnitem.id,self.getPid()))
                break
            elif self.isFatalError:
                print("vpn 连接失败")
                break
            elif self.isAUTH_FAILED_EXITING:
                print("vpn 认证失败")
                break
            time.sleep(1)

        self.logger.debug("连接日志:")
        with open(self.logfilepath,'r') as f:
            self.logger.debug(f.read())
        return self
    
    
    

    def isProcesslive(self):
        """openvpn 进程是否活跃, 通常这用于判断当前的连接状态"""
        return psutil.pid_exists(self.getPid())

    def parseOpenvpnlog(self):
        lines = []
        with open(self.logfilepath,'r') as f:
            lines = f.readlines()

        text = '\n'.join(lines)

        self.isOk = False
        self.isConnected = False

        #是否失败
        match = re.search(r"Exiting due to fatal error", text)
        if match:
            self.logger.debug("找到连接失败文字:Exiting due to fatal error")    
            self.isOk=False   
            self.isFatalError = True    # 确定连接不上,不用等了

        match = re.search(r"Initialization Sequence Completed", text)
        if match:
            self.isConnected=True
            self.isOk = True

        match = re.search(r"SIGTERM\[soft,auth-failure\] received, process exiting", text)
        if match:
            #因认证失败而退出
            self.isAUTH_FAILED_EXITING=True
            self.isOk = False

        
            

        # 通道名称
        match = re.search(r"TUN/TAP device (.*) opened", text)
        if match:
            self.tunName = match.groups()[0]
            self.logger.debug("识别到通道名：{}".format(self.tunName))

    def parseOvpnConfig(self):
        def getvolum(name):

            text = re.sub("\r","",self.vpnitem.ovpn_config_text)
            r = r"^[^#;]"+name+" (.*)"
            match = re.search(r, text, re.MULTILINE)
            if match:

                self.logger.debug("[DEBUG]ovpn配置 {}: {}".format(name,match.groups()[0]))
                return match.groups()[0]
        
        self.serverProto = getvolum("proto")    
        self.serverHost, self.serverPort = getvolum("remote") .split(' ')
        self.serverPort = int(self.serverPort)
 
    def getPid(self):
        """获取进程ID"""

        def tryReadPidFromfile():
            with open(self.openvpn_pidpath,'r') as f:
                line = f.readline()
                if len(line.strip()) == 0:
                    logger.debug("文件{}不应该没有文字".format(self.openvpn_pidpath))
                    return None
                return int(line)

        if self.pid is None:
            """因为openvpn进程是数据外部进程，不能确定它什么时候启动，所以，多试几次"""
            trycount = 5
            while trycount>0:
                self.pid  = tryReadPidFromfile()
                if self.pid is not None:
                    break
                time.sleep(1)                                
                trycount = trycount -1
                if trycount == 0:
                    raise Exception("无法读取openvpn pid")
            
        return self.pid

    def startupOpenvpnDeamon(self):
        config_content = self.vpnitem.ovpn_config_text
        with open(self.openvpn_configpath,'w') as f:
            f.write(config_content)
            f.close()

        #参数说明：
        #    --route-nopull 可以考虑，不过后来试了一下，发现有问题。问题原因不太肯定。
        openvpn_cmd = """openvpn --connect-retry 1 --connect-retry-max {}  --auth-nocache --config {}  --daemon {}  --log {} --writepid {}    --dev {}  --status {} 1 """.format(
            VPN_CONNECT_RETRY_MAX, 
            self.openvpn_configpath,
            "openvpndeamon-"+str(self.vpnitem.id), 
            self.logfilepath,
            self.openvpn_pidpath,
            self.tunName,
            self.openvpn_status_path)
        self.logger.debug("启动命令：{}".format(openvpn_cmd))
        subprocess.call(shlex.split(openvpn_cmd))

        
        
class VpnCheck:
    def check_avriable(self, *vpnitems):
        """检查vpn是否能够连接，多个vpn是并行的"""

        self.connections = [VpngateSession(item).connect()
                                for item in vpnitems
                                ]
        time.sleep(20)
        for conn in self.connections:
            if conn.isConnected():
                """能连接的"""
                #TODO:写入数据库中
                logger.debug("检测结果：能连接")
                status=VpnStatus(last_check_at=timezone.now(), last_up_at=timezone.now(),last_check_status="ok")
                status.save()
                conn.vpnitem.status = status
                conn.vpnitem.save()
            else:
                #TODO:写入数据库
                logger.debug("检测结果：不能连接")
                status=VpnStatus(last_check_at=timezone.now(), last_up_at=timezone.now(),last_check_status="fail")
                status.save()
                conn.vpnitem.status = status
                conn.vpnitem.save()
            conn.disconnect()
