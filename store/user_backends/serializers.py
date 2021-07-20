from rest_framework import serializers
from user_backends import models as user_models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = ['id', 'email', 'balance', 'password']
        extra_kwargs = {
            'balance': {'read_only': True},
            'password': {'write_only': True}
        }
