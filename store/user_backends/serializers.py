from rest_framework import serializers
import models as user_models


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = ['id', 'email', 'balance']