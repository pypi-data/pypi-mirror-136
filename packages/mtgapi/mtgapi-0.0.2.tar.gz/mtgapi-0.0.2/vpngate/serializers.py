from rest_framework import fields, serializers
from .models import VpnConnect, VpnItem
class VpnConnectSerializer(serializers.ModelSerializer):
    class Meta:
        model = VpnConnect
        fields = ["uptime", "logfilepath","pid", "logtext"]

class VpnItemSerializer(serializers.ModelSerializer):   

    # 外键信息JSON对象直接嵌套。
    # 参考文章：https://www.django-rest-framework.org/api-guide/relations/
    connectinfo = VpnConnectSerializer(many=False, read_only=True)    
    # connection_status = serializers.SerializerMethodField() 

    # def get_connection_status(self, vpnitem):
    #     """附加连接信息给前端"""        
    #     return VpnConnectionManager.getStatus(vpnitem)

    class Meta:
        model = VpnItem
        # fields = ['id','hostname', 'ip','country_short','speed','score',
        # 'ping','country_short','num_vpn_sessions','total_users',
        # 'total_traffic','logtype','operator',
        # 'message','connectinfo'
        # ]
        # fields = ["hostname","connectinfo","country_short"]

        fields='__all__'

        # fields=["id","connectinfo","connection_status"]
    

 


    # def get_connect_info(self, obj):
    #         return obj.connect_info



# class TrackSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Track
#         fields = ['order', 'title', 'duration']

# class AlbumSerializer(serializers.ModelSerializer):
#     tracks = TrackSerializer(many=True, read_only=True)

#     class Meta:
#         model = Album
#         fields = ['album_name', 'artist', 'tracks']