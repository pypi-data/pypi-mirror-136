from django.db import models


from datetime import datetime

from django.utils import timezone


class VpnConnect(models.Model):
    """表示当前的连接信息，注意，是实际当下的连接，一条记录必定对应一个进程，一个通道。"""
    uptime = models.DateTimeField(help_text="初次启动时间", default=timezone.now)
    logfilepath = models.CharField(max_length=100, help_text="日志文件路径(过时)")
    logtext = models.TextField(
        null=True, default=None, help_text="openvpn输出的日志文本")
    pid = models.IntegerField(null=True, help_text="进程id")
    tunnel_name = models.CharField(max_length=100,null=False, help_text="通道名，形如“tun0”,跟网卡名对应")
    is_gate_way = models.BooleanField(default=False, help_text="是否默认网关")

    # def __str__(self):
    #     return '%d: %s' % (self.pid, self.status)


class VpnStatus(models.Model):
    # 更加详细的vpn服务器信息
    last_check_at = models.DateTimeField(auto_now_add=True,
                                         help_text="最后一次检测时间")
    last_up_at = models.DateTimeField(
        null=True,
        help_text="最后一次成功连接时间", default=timezone.now)
    # last_check_status = models.CharField(max_length=20, help_text="最后连接的状态")
    isUp = models.BooleanField(null=True, help_text="是否能连接，null 未知，True能，False，不能")

class VpnOvpn(models.Model):
    """表示ovpn的关键配置信息"""
    host = models.CharField(max_length=50, help_text="主机名称")
    port  = models.IntegerField(null=False, help_text="端口")
    proto = models.CharField(max_length=10, null=False, help_text="协议: tcp | udp")

class HostCheck(models.Model):
    """表示对一个主机的检测情况"""
    host_name = models.CharField(max_length=50, help_text="主机名称")
    ipv4  = models.CharField(max_length=16, null=False, help_text="IP地址字符")

class HostCheckPort(models.Model):
    """对主机端口检测情况记录"""
    ipv4 = models.CharField(max_length=16, null=False, help_text="IP地址字符")
    proto = models.CharField(max_length=10, null=False, help_text="协议: tcp | udp")
    port = models.IntegerField(null=False, help_text="端口号")

class VpnItem(models.Model):
    connectinfo = models.ForeignKey(
        VpnConnect, related_name='connectinfo2', on_delete=models.CASCADE, null=True, help_text="当前连接信息")
    # status = models.ForeignKey(
    #     VpnStatus, related_name='status', on_delete=models.CASCADE, null=True, help_text="vpn服务器状态")
    ovpnconfig = models.ForeignKey(
        VpnOvpn, related_name='ovpn', on_delete=models.CASCADE, null=True, help_text="ovpn配置信息")
    hostname = models.CharField(max_length=200)
    ip = models.CharField(max_length=200)
    score = models.CharField(max_length=200)
    ping = models.CharField(max_length=200)
    speed = models.CharField(max_length=200)
    country_long = models.CharField(max_length=200)
    country_short = models.CharField(max_length=200)
    num_vpn_sessions = models.IntegerField(null=True)
    uptime = models.BigIntegerField(null=True)
    total_users = models.IntegerField(null=True)
    total_traffic = models.BigIntegerField(null=True)
    logtype = models.CharField(max_length=200)
    operator = models.CharField(max_length=200)
    message = models.CharField(max_length=200)
    ovpn_config_text = models.TextField()

    #附加几个复制字段
    createat = models.DateTimeField(auto_now_add=True)
    updateat = models.DateTimeField(auto_now=True)


# class Album(models.Model):
#     album_name = models.CharField(max_length=100)
#     artist = models.CharField(max_length=100)


# class Track(models.Model):
#     album = models.ForeignKey(
#         Album, related_name='tracks', on_delete=models.CASCADE)
#     order = models.IntegerField()
#     title = models.CharField(max_length=100)
#     duration = models.IntegerField()

#     class Meta:
#         unique_together = ['album', 'order']
#         ordering = ['order']

#     def __str__(self):
#         return '%d: %s' % (self.order, self.title)
