from rest_framework import viewsets, pagination
import serializers as user_serializers
import models as user_models


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = user_serializers.UserSerializer
    queryset = user_models.User.objects.all()
    pagination_class = pagination.LimitOffsetPagination
