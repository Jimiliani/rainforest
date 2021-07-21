from django_filters import rest_framework as filters
from api import models as api_models


class ItemsStatisticsFilter(filters.FilterSet):
    sold_at = filters.DateFromToRangeFilter(field_name='orders__sold_at')

    class Meta:
        model = api_models.Item
        fields = []
