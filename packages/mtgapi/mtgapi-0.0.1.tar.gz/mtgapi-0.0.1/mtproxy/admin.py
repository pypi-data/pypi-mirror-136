from django.contrib import admin
from . import models


admin.site.register(models.SysConfig)
admin.site.register(models.SysSettings)
admin.site.register(models.PortForward)
admin.site.register(models.SshHost)
admin.site.register(models.Ovpn)
admin.site.register(models.Bot)
admin.site.register(models.PrivateKey)
admin.site.register(models.Script)
admin.site.register(models.Onion)
admin.site.register(models.BotLog)
admin.site.register(models.SiteConfig)
admin.site.register(models.MtxPlugin)
