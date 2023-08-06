from django.contrib import admin
from .models import VpnItem, VpnConnect
from . import models
# Register your models here.


class VpnItemAdmin(admin.ModelAdmin):
    pass


admin.site.register(VpnItem, VpnItemAdmin)


class VpnConnectAdmin(admin.ModelAdmin):
    pass


admin.site.register(VpnConnect, VpnConnectAdmin)


# class TracktAdmin(admin.ModelAdmin):
#     pass


# admin.site.register(models.Track, TracktAdmin)


# class AlbumAdmin(admin.ModelAdmin):
#     pass


# admin.site.register(models.Album, AlbumAdmin)
