from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins

from api import serializer as api_serializers
from api import models as api_models
from user_backends import models as user_models


class TopUpBalanceViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.ListModelMixin):
    serializer_class = api_serializers.TopUpBalanceSerializer
    queryset = user_models.User.objects.all()

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(user_models.User, pk=pk)


class ItemViewSet(viewsets.ModelViewSet):
    serializer_class = api_serializers.ItemSerializer
    queryset = api_models.Item.objects.all()

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(api_models.Item, pk=pk)
