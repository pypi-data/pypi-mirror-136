# from turtle import title
from django.db import models
from django.conf import settings


class SysConfig(models.Model):
    """核心配置"""
    host=models.CharField(max_length=64, null=False, blank=False, default=None, verbose_name = "项名")
    private_key=models.TextField(null=True, blank=True, default="", verbose_name = "系统专用私钥")
    public_key=models.TextField(null=True, blank=True, default="", verbose_name = "系统专用私钥对应公钥")
    
    def __str__(self) -> str:
        return f"{self.host}"
    class Meta(object):
        verbose_name = '核心配置'
        verbose_name_plural = verbose_name

class SysSettings(models.Model):
    """系统配置"""
    key=models.CharField(max_length=64, null=False, blank=False, default=None, verbose_name = "项名")
    value=models.CharField(max_length=64, null=False, blank=False, default="", verbose_name = "项值")
    verbose = models.CharField(max_length=64, null=True, blank=True, default=None, verbose_name = "描述")
    def __str__(self) -> str:
        return f"{self.key}:{self.value} {self.verbose}"
    class Meta(object):
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name

class SiteConfig(models.Model):
    """系统配置"""
    site_name=models.CharField(max_length=64, unique=True, null=False, blank=False, default=None, verbose_name = "站点域名")
    onion_key=models.CharField(max_length=130, null=False, blank=False, default=None, verbose_name = "站点onion私钥")
    onion=models.CharField(max_length=70, null=False, blank=False, default=None, verbose_name = "onion域名")    
    
    def __str__(self) -> str:
        return f"{self.site_name}:{self.onion}"
    class Meta(object):
        verbose_name = '站点配置'
        verbose_name_plural = verbose_name



class SshHost(models.Model):
    """SSH服务器信息"""
    title = models.CharField(max_length=64, null=True, blank=True, default=None, verbose_name = "备注")
    host = models.CharField(max_length=64, verbose_name = "主机名")
    port = models.IntegerField(default=22, verbose_name = "端口")
    user = models.CharField(max_length=32, verbose_name = "用户名")
    password = models.CharField(max_length=32, verbose_name = "密码")
    private_key = models.TextField(null=True, blank=True, default=None, verbose_name="私钥")
    tag = models.CharField(max_length=16, null=True, blank=True, default=None, verbose_name="标签分类")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self) -> str:
        return f"{self.title} : ssh {self.user}@{self.host} -p {self.password}"

    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = 'SSH主机'
        verbose_name_plural = verbose_name

class PortForward(models.Model):
    """
    端口转发
    """
    PROTOCOL_TYPE = (
        ("tcp","tcp"),
        ("udp","udp")
    )
    title = models.CharField(max_length=64, null=True, blank=True, default="[new]", verbose_name = "备注")
    lhost = models.CharField(max_length=64, default='0.0.0.0',verbose_name = "本机IP")
    lport = models.IntegerField(blank=False, null=False, verbose_name = "本机端口")
    rhost = models.CharField(max_length=32, blank=False, null=False, verbose_name = "远程IP")
    rport = models.IntegerField(blank=False, null=False, verbose_name = "远程端口")
    proto = models.CharField(max_length=32, choices=PROTOCOL_TYPE, default="tcp", verbose_name="网络协议类型",null=True,blank=True)
    via_ssh = models.ForeignKey(to=SshHost,on_delete = models.DO_NOTHING,verbose_name = "通过ssh隧道")
    enabled = models.BooleanField(default=True, verbose_name = "启用")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f"{self.title} {self.proto}://{self.lhost}:{self.lport}/{self.rhost}:{self.rport}"
    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = '端口转发'
        verbose_name_plural = verbose_name


class Ovpn(models.Model):
    PROTOCOL_TYPE = (
        ("tcp","tcp"),
        ("udp","udp")
    )
    title = models.CharField(max_length=64, null=True, blank=True, default="[new ovpn]", verbose_name = "备注")
    host = models.CharField(max_length=64, null=False, blank=False, default="127.0.0.1", verbose_name = "服务器地址")
    port = models.IntegerField(verbose_name = "端口",null=False, blank=False, default=1194)
    protocol = models.CharField(max_length=12, null=False, blank=False, choices=PROTOCOL_TYPE, default="tcp", verbose_name = "协议类型")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    enabled = models.BooleanField(default=True, verbose_name = "启用")
    def __str__(self) -> str:
        return f"{self.title} {self.host}:{self.port} {self.protocol}"

    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = 'OVPN'
        verbose_name_plural = verbose_name

class Onion(models.Model):
    """隐藏域名的私钥对应域名名称"""
    tag=models.CharField(max_length=64, null=True, blank=True, default="default", verbose_name = "标签")
    private_key=models.CharField(max_length=1024, null=True, blank=True, verbose_name = "私钥")
    service_port=models.IntegerField(verbose_name = "服务端口",null=False, blank=False, default=80)
    target_host=models.CharField(max_length=32, null=False, blank=False, default="127.0.0.1", verbose_name = "主机名")
    target_port=models.IntegerField(verbose_name = "目标",null=False, blank=False, default=80)
    # title = models.CharField(max_length=64, null=True, blank=True, default="[new onion]", verbose_name = "备注")
    #过时
    # hs_ed25519_secret_key = models.CharField(max_length=128, null=False, blank=False, verbose_name = "base64编码的私钥")
    #过时
    # hs_ed25519_pub_key = models.CharField(max_length=128, null=True, blank=True, verbose_name = "base64编码的公钥")
    onion=models.CharField(max_length=64, null=False, blank=False, verbose_name = "onion域名")

    def __str__(self) -> str:
        return f"{self.tag} {self.service_port}:{self.target_host} {self.target_port}, {self.onion}"
    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = 'onion服务'
        verbose_name_plural = verbose_name    

class OnionBot(models.Model):
    """ onion ssh 肉鸡"""
    title = models.CharField(max_length=64, null=True, blank=True, default="[new onion]", verbose_name = "备注")
    hs_ed25519_secret_key = models.CharField(max_length=128, null=False, blank=False, verbose_name = "base64编码的私钥")
    hs_ed25519_pub_key = models.CharField(max_length=128, null=True, blank=True, verbose_name = "base64编码的公钥")
    onion=models.CharField(max_length=64, null=False, blank=False, verbose_name = "onion域名")


class PrivateKey(models.Model):
    PRIVATE_KEY_TYPE = (
        ("rsa","rsa"),
        ("ed25519","ed25519"),
    )
    title = models.CharField(max_length=64, null=True, blank=True, default=None, verbose_name = "备注")
    type = models.CharField(max_length=64, null=True, blank=True, choices=PRIVATE_KEY_TYPE, default="rsa", verbose_name = "类型")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="用户")
    privatekey = models.CharField(max_length=4096, null=False, blank=False, verbose_name = "私钥值")
    public = models.CharField(max_length=4096, null=False, blank=False, verbose_name = "公钥值")
    def __str__(self) -> str:
        return f"{self.type} {self.title}"

    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = '私钥'
        verbose_name_plural = verbose_name

class Bot(models.Model):
    """肉鸡"""
    BOT_TYPE = (
        ("ssh","ssh"),
        ("webshell","webshell")
    )
    title = models.CharField(max_length=64, null=True, blank=True, default=None, verbose_name = "备注")
    type = models.CharField(max_length=64, null=True, blank=True, choices=BOT_TYPE, default=None, verbose_name = "类型")
    host = models.CharField(max_length=64, verbose_name = "主机名")
    port = models.IntegerField(default=22, verbose_name = "端口")
    user = models.CharField(max_length=32, verbose_name = "用户名")
    password = models.CharField(max_length=32, verbose_name = "密码")
    private_key_text = models.TextField(null=True, blank=True, default=None, verbose_name="私钥")
    private_key = models.ForeignKey(PrivateKey, null=True, blank=True, on_delete=models.DO_NOTHING)
    tag = models.CharField(max_length=16, null=True, blank=True, default=None, verbose_name="标签分类")
    is_live = models.BooleanField(null=False, blank=False, default=False, verbose_name="是否在线")
    last_check = models.DateTimeField(auto_now=True, verbose_name="最新检测时间")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="用户")
    
    def __str__(self) -> str:
        return f"{self.title} : {self.type}@{self.host}"

    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = '肉鸡'
        verbose_name_plural = verbose_name

class BotLog(models.Model):
    type = models.CharField(max_length=64, null=True, blank=True,  default=None, verbose_name = "操作类型")
    content = models.TextField(null=True, blank=True, default=None, verbose_name = "操作日志")
    timestamp = models.DateTimeField(auto_now_add=True, blank=False, null=False, verbose_name="时间搓")
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, verbose_name="肉鸡")

    def __str__(self) -> str: 
        return f"{self.type} : {self.timestamp} {self.content[:30]}"

    class Meta(object):
        verbose_name = '肉鸡日志'
        verbose_name_plural = verbose_name


class Script(models.Model):
    """脚本"""
    SCRIPT_TYPE = (
        ("bash","bash"),
        ("python","python")
    )
    title = models.CharField(max_length=64, null=True, blank=True, default="[new script]", verbose_name = "备注")
    type=models.CharField(max_length=16, null=False, blank=False,choices=SCRIPT_TYPE, verbose_name="脚本类型")
    content = models.TextField(null=False,blank=False, verbose_name = "脚本内容")
    markdown_content = models.TextField(null=True,blank=True, verbose_name = "辅助内容")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="用户")
    def __str__(self) -> str:
        return f"{self.type} {self.title}"
    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = '脚本'
        verbose_name_plural = verbose_name

class MtxPlugin(models.Model):
    """插件管理
        原理：插件源码位于git仓库。 模型记录仓库的配置，安装脚本。
    """
    MTXPLUGIN_TYPE = (
        ("github","github"),
        ("curl","curl")
    )
    title = models.CharField(max_length=64, null=True, blank=True, default="[new script]", verbose_name = "标题")
    type=models.CharField(max_length=16, null=False, blank=False,choices=MTXPLUGIN_TYPE, verbose_name="插件类型")
    src=models.CharField(max_length=1024, null=False, blank=False,verbose_name="源码地址")
    installscript = models.TextField(null=False,blank=False, verbose_name = "安装脚本")
    markdown_content = models.TextField(null=True,blank=True, verbose_name = "辅助内容")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, verbose_name="用户")
    def __str__(self) -> str:
        return f"{self.type} {self.title}"
    class Meta(object):
        # 定义表名
        # db_table = "department"
        # 定义在管理后台显示的名称
        verbose_name = '插件'
        verbose_name_plural = verbose_name

