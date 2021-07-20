from rest_framework import serializers

from user_backends.models import User


class TopUpBalanceSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(min_value=0)

    class Meta:
        model = User
        fields = ['amount', ]

    def update(self, instance, validated_data):
        instance.amount += validated_data['amount']
        instance.save()
        return instance
