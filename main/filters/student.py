from django.utils.translation import gettext_lazy as _

from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters

from .. import models


class StudentFilter(FilterSet):
    has_loan = filters.BooleanFilter(method='get_has_loan', label=_('Has loan'))

    class Meta:
        model = models.Student
        fields = {
            'phone': ['exact'],
        }

    def get_has_loan(self, queryset, field_name, value: bool, *args, **kwargs):
        if value:
            return queryset.filter(balance__lt=0)
        return queryset.filter(balance__gte=0)

