from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, pagination, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api import serializer as api_serializers
from api import models as api_models
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
    queryset = api_models.Item.objects.all()
    pagination_class = pagination.LimitOffsetPagination

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(api_models.Item, pk=pk)


class OrderViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    serializer_class = api_serializers.OrderSerializer
    queryset = api_models.Order.objects.all()
    pagination_class = pagination.LimitOffsetPagination

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(api_models.Order, pk=pk)

    @action(methods=['POST'], detail=True)
    def pay(self):
        instance = self.get_object()
        instance.pay(instance.owner)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True, url_path='return')
    def return_order(self):
        instance = self.get_object()
        instance.return_order(instance.owner)
        return Response(status=status.HTTP_200_OK)


class ItemInOrderRelationshipViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.DestroyModelMixin):
    serializer_class = api_serializers.ItemInOrderRelationshipSerializer
    queryset = api_models.ItemInOrderRelationship.objects.all()

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(api_models.ItemInOrderRelationship, pk=pk)
