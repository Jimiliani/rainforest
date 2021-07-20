from django import forms
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, pagination
import serializers as user_serializers
import models as user_models


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = user_serializers.UserSerializer
    queryset = user_models.User.objects.all()
    pagination_class = pagination.LimitOffsetPagination

    def get_object(self):
        validator = forms.IntegerField()
        pk = validator.to_python(self.kwargs.get('pk', 0))
        return get_object_or_404(user_models.User, pk=pk)


