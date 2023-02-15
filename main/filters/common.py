from copy import deepcopy

from django.contrib.admin.filters import SimpleListFilter
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.forms import SimpleArrayField
from django.db.models import Q
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend


class ArrayFilter(filters.filters.Filter):
    """
    Array filter to tell filterset about  base field class for lookups.
    """
    base_field_class = SimpleArrayField


class PostgresFieldFilterSet(filters.FilterSet):
    """
    As per the code, default filters are placed in FILTER_DEFAULTS.
    This code is updating the FILTER_DEFAULTS and appending Custom Fields (ArrayField)
    for consideration.
    """
    FILTER_DEFAULTS = deepcopy(filters.filterset.FILTER_FOR_DBFIELD_DEFAULTS)
    FILTER_DEFAULTS.update({
        ArrayField: {
            'filter_class': ArrayFilter,
        },
    })


class FilterBackend(DjangoFilterBackend):
    """
    FilterBackend with PostgresFieldFilterSet as the default filter_set.
    """
    default_filter_set = PostgresFieldFilterSet


class InputFilter(SimpleListFilter):
    template = 'admin/input_filter.html'

    def queryset(self, request, queryset):
        term = self.value()
        if term is None:
            return
        any_name = Q()
        if hasattr(self, 'filter_key'):
            for bit in term.split():
                any_name &= (
                    Q(**{self.filter_key: bit})
                )
        return queryset.filter(any_name)

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return (),

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice
