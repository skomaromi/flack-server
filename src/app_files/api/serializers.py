from rest_framework import serializers

from ..models import File


class FileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
