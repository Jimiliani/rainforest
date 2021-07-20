from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins

from api.serializer import TopUpBalanceSerializer
from user_backends.models import User


class TopUpBalanceViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin, mixins.ListModelMixin):
    serializer_class = TopUpBalanceSerializer
    queryset = User.objects.all()

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(User, pk=pk)

