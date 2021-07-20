from rest_framework import serializers

import models as api_models

from user_backends import models as user_models


class TopUpBalanceSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField(min_value=0)

    class Meta:
        model = user_models.User
        fields = ['amount', ]

    def update(self, instance, validated_data):
        instance.amount += validated_data.get('amount', instance.amount)
        instance.save()
        return instance


class ItemMassActionsSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        books = [api_models.Item(**item) for item in validated_data]
        return api_models.Item.objects.bulk_create(books)

    def update(self, instance, validated_data):
        item_mapping = {item.id: item for item in instance}
        data_mapping = {item['id']: item for item in validated_data}

        ret = []
        for item_id, data in data_mapping.items():
            item = item_mapping.get(item_id, None)
            if item is not None:
                ret.append(self.child.update(item, data))

        return ret


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = api_models.Item
        fields = ['name', 'prime_cost', 'cost', 'amount']
        list_serializer_class = ItemMassActionsSerializer

