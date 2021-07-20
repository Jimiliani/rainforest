from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api import models as api_models

from user_backends import models as user_models


class TopUpBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = ['id', 'balance']

    def update(self, instance, validated_data):
        instance.balance += validated_data.get('balance', instance.balance)
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
        fields = ['id', 'name', 'prime_cost', 'cost', 'amount']
        list_serializer_class = ItemMassActionsSerializer


class ItemInOrderRelationshipSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=api_models.Item.objects.all())
    order = serializers.PrimaryKeyRelatedField(queryset=api_models.Order.objects.all())

    class Meta:
        model = api_models.ItemInOrderRelationship
        fields = ['id', 'item', 'order', 'amount']


class ItemInOrderRelationshipReadOnlySerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)

    class Meta:
        model = api_models.ItemInOrderRelationship
        fields = ['id', 'item', 'amount']


class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=user_models.User.objects.all())
    items_in_order = ItemInOrderRelationshipReadOnlySerializer(read_only=True, many=True)

    class Meta:
        model = api_models.Order
        fields = ['id', 'owner', 'items_in_order']


class OrderCreationItemsSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=api_models.Item.objects.all())

    class Meta:
        model = api_models.ItemInOrderRelationship
        fields = ['item', 'amount']

    def create(self, validated_data):
        pass

class CreateOrderSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=user_models.User.objects.all())
    items_in_order = OrderCreationItemsSerializer(many=True)

    class Meta:
        model = api_models.Order
        fields = ['id', 'owner', 'items_in_order']

    def create(self, validated_data):
        items = validated_data.pop('items_in_order', [])
        instance = api_models.Order.objects.create(**validated_data)
        items_ = [api_models.ItemInOrderRelationship(**item, order=instance) for item in items]
        try:
            with transaction.atomic():
                for item in items_:
                    item.save()  # not using bulk_create because save method won't be called
        except ValidationError as e:
            instance.delete()
            raise e
        return instance or None
