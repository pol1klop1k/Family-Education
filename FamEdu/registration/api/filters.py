from django.db.models import Q
from django_filters import rest_framework as filters

from registration.models import (
    Child
)


class StudentFilterSet(filters.FilterSet):
    search = filters.CharFilter(method="filter_creds")
    grade = filters.NumberFilter()

    class Meta:
        model = Child
        fields = ["search", "grade"]

    def filter_creds(self, queryset, name, value):
        return self.queryset.filter(
            Q(name__icontains=value) |
            Q(surname__icontains=value) |
            Q(patronymic__icontains=value),
        )
