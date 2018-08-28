from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class LoginModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'password'
        ]


class UserModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username'
        ]
