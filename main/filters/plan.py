from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters

from .. import models


class PlanFilter(FilterSet):
    student = filters.ModelChoiceFilter(
        queryset=models.Student.objects,
        method='by_student',
        label=_('student'),
    )
    group = filters.ModelChoiceFilter(
        queryset=models.Group.objects,
        method='by_group',
        label=_('group'),
    )

    class Meta:
        model = models.Plan
        fields = ('student',)

    def by_student(self, queryset, field_name, value, *args, **kwargs):
        return queryset.filter(created_at__year__gte=value.created_at.year - 1)

    def by_group(self, queryset, field_name, value, *args, **kwargs):
        print(queryset, flush=True)
        result = queryset.filter(max_student_count=value.max_student_count)
        print(result, flush=True)
        print(value, flush=True)
        print(value.max_student_count, flush=True)
        return result
