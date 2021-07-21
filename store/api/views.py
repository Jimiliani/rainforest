from django import forms
from django.db.models import F, Sum, Prefetch, Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, pagination, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db import models as django_models
from api import serializer as api_serializers
from api import models as api_models
from api import filters
from user_backends import models as user_models


class TopUpBalanceViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = api_serializers.TopUpBalanceSerializer
    queryset = user_models.User.objects.all()

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(user_models.User, pk=pk)


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.ItemSerializer
    filterset_class = filters.ItemsStatisticsFilter

    def get_queryset(self):
        if self.action == 'statistics':
            items = api_models.Item.objects.annotate(
                proceed=F('cost') * Sum('orders_with_item__amount', filter=Q(orders_with_item__order__paid=True), output_field=django_models.PositiveIntegerField()),
                profit=(F('cost') - F('prime_cost')) * Sum('orders_with_item__amount', filter=Q(orders_with_item__order__paid=True), output_field=django_models.PositiveIntegerField()),
                sold_count=Sum('orders_with_item__amount', filter=Q(orders_with_item__order__paid=True))
            ).only('id', 'name', 'returned_amount')
            return items
        return api_models.Item.objects.all()

    def get_serializer_class(self):
        if self.action == 'statistics':
            return api_serializers.ItemStatisticsSerializer
        return api_serializers.ItemSerializer

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(api_models.Item, pk=pk)

    @action(methods=['GET'], detail=False)
    def statistics(self, *args, **kwargs):
        serializer = self.get_serializer(self.paginate_queryset(self.filter_queryset(self.get_queryset())), many=True)
        return self.get_paginated_response(serializer.data)


class OrderViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    queryset = api_models.Order.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return api_serializers.CreateOrderSerializer
        elif self.action not in ['pay', 'return_order']:
            return api_serializers.OrderSerializer

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(api_models.Order, pk=pk)

    @action(methods=['POST'], detail=True)
    def pay(self, *args, **kwargs):
        instance = self.get_object()
        instance.pay(instance.owner)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='return')
    def return_order(self, *args, **kwargs):
        instance = self.get_object()
        instance.return_order(instance.owner)
        return Response(status=status.HTTP_200_OK)


class ItemInOrderRelationshipViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    serializer_class = api_serializers.ItemInOrderRelationshipSerializer
    queryset = api_models.ItemInOrderRelationship.objects.all()

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(api_models.ItemInOrderRelationship, pk=pk)
