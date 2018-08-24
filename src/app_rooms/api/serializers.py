from rest_framework import serializers

from ..models import Room


class RoomModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id',
            'name',
            'time_created',
            'participants',
        ]
