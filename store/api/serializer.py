from django.db import transaction, IntegrityError
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


class CreateOrderSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=user_models.User.objects.all())

    class Meta:
        model = api_models.Order
        fields = ['id', 'owner']

    def create(self, validated_data):
        items_in_order = self.initial_data.get('items_in_order', [])
        try:
            with transaction.atomic():
                order = api_models.Order.objects.create(**validated_data)

                not_created_items_relations = [
                    api_models.ItemInOrderRelationship(
                        item_id=item['item'], amount=item['amount'], order=order
                    ) for item in items_in_order
                ]
                created_items_relations = api_models.ItemInOrderRelationship.objects.bulk_create(
                    not_created_items_relations)

                item_id_to_amount_converter = dict(
                    map(lambda item: (item.item_id, item.amount), created_items_relations))

                items = list(order.items.only('id', 'amount').all())
                for item in items:
                    item.amount -= item_id_to_amount_converter[item.id]
                api_models.Item.objects.bulk_update(items, fields=['amount'])
        except IntegrityError:
            raise ValidationError("Not enough items for creating order")

        return order


class ItemStatisticsSerializer(serializers.ModelSerializer):
    returned_amount = serializers.IntegerField()
    proceed = serializers.IntegerField()
    profit = serializers.IntegerField()
    sold_count = serializers.IntegerField()

    class Meta:
        model = api_models.Item
        fields = ['id', 'name', 'returned_amount', 'proceed', 'profit', 'sold_count']
