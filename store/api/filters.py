from django_filters import rest_framework as filters
from api import models as api_models


class ItemsStatisticsFilter(filters.FilterSet):
    class Meta:
        model = api_models.Item
        fields = ['sold_at']
