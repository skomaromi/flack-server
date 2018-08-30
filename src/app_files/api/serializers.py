import humanize
from netifaces import interfaces, ifaddresses, AF_INET

from rest_framework import serializers

from ..models import File


class FileModelSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    localnode_url = serializers.SerializerMethodField()
    shareable_url = serializers.SerializerMethodField()
    hash = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = [
            'name',
            'size',
            'localnode_url',
            'shareable_url',
            'id',
            'hash'
        ]

    def get_size(self, obj):
        return humanize.naturalsize(obj.file.size)

    def get_localnode_url(self, obj):
        local_ip = None

        for iface in interfaces():
            if_addrs = ifaddresses(iface).get(AF_INET)
            if if_addrs is not None:
                addr = if_addrs[0].get('addr')
                if addr != '127.0.0.1':
                    local_ip = addr

        if local_ip is None:
            local_ip = '127.0.0.1'

        return 'http://{local_ip}:8080/ipfs/{multihash}/{filename}'.format(
            local_ip=local_ip, multihash=obj.file.name, filename=obj.name
        )

    def get_shareable_url(self, obj):
        return obj.file.url

    def get_hash(self, obj):
        return obj.file.name
