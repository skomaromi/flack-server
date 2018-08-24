from rest_framework import serializers

from ..models import Message


class MessageModelSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = '__all__'

    def get_location(self, obj):
        if obj.location:
            # keeping it ISO 6709
            return {'latitude': obj.location.lat, 'longitude': obj.location.lon}
        return None

    def get_file(self, obj):
        if obj.file:
            return {'name': obj.file.name, 'url': obj.file.file.url}
        return None

    def get_sender(self, obj):
        return obj.sender.username
