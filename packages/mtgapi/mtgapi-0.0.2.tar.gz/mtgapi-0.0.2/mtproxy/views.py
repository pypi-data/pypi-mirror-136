from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from .models import PortForward
from . import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from git import Repo
from pathlib import Path


def index(request):
    return render(request,'mtproxy/index.html')

def vpnconnect(r):
    """返回让debian系统连接vpn服务器的脚本"""
    data_dict = {
        "vpnserver_host":"0.0.0.0",
        "vpnserver_port": 1194,
        "vpnserver_proto": "tcp",
        "vpn_user":"win9",
        "vpn_password": "feihuo321"
    }
    return render(r,"mtproxy/vpn/connect.sh", data_dict)

def onion_ssh_bot_up(request):
    """一次性脚本，让受控主机成为onionSsh肉鸡"""
    return render(request, "mtproxy/onionsshbot/onion_ssh_up.sh")

def mtaction_script(request):
    return render(request, "mtproxy/mtaction/docker_entry.sh")

def script_content(request):
    """返回可执行脚本"""
    script_model = models.Script.objects.get(pk=request.GET.get("id"))
    if script_model:
        content:str = script_model.content
        content = content.replace("\r","")
        return HttpResponse(content)
    else:
        return HttpResponse("")

def git_run(request):
    """克隆仓库源码并安装到本地"""
    print("asdfadf")
    git_url = request.GET.get("giturl","")
    # git_dir = Path("./gittest11")
    # # if 'libclang' in autowig.parser:
    # #     autowig.parser.plugin = 'libclang'
    # # cls.srcdir = Path('fp17')
    # if not git_dir.exists():
    #     Repo.clone_from('https://github.com/StatisKit/FP17.git', git_dir.relpath('.'), recursive=True)
    # # cls.srcdir = cls.srcdir/'share'/'git'/'ClangLite'
    # # cls.incdir = Path(sys.prefix).abspath()
    # # if any(platform.win32_ver()):
    # #     cls.incdir = cls.incdir/'Library'
    # # subprocess.check_output(['scons', 'cpp', '--prefix=' + str(cls.incdir)],
    # #                         cwd=cls.srcdir)
    # # if any(platform.win32_ver()):
    # #     cls.scons = subprocess.check_output(['where', 'scons.bat']).strip()
    # # else:
    # #     cls.scons = subprocess.check_output(['which', 'scons']).strip()
    # # cls.incdir = cls.incdir/'include'/'clanglite' 

    return HttpResponse(git_url)


    


##
## 演示接收各种系统信号。
##
@receiver(pre_save, sender=PortForward)
def my_handler(sender, **kwargs):
    print("信号,", flush=True)
    print(sender)
    print(kwargs)

