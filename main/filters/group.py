from django.db.models import Count, F
from django.utils.translation import gettext_lazy as _
from django_filters.rest_framework import FilterSet
from django_filters import rest_framework as filters

from .. import models
from .. import choices


class GroupFilter(FilterSet):
    completeness = filters.ChoiceFilter(
        choices=(
            ('not_enough', _('Not enough')),
            ('complete', _('Complete')),
            ('over', _('Over')),
        ),
        label=_('Completeness'),
        method='by_student',
    )

    current_teacher = filters.ModelChoiceFilter(
        queryset=models.User.objects.filter(role=choices.Role.TEACHER),
    )
    student = filters.ModelChoiceFilter(
        label=_('student'),
        queryset=models.Student.objects.all(),
        method='by_student',
    )

    class Meta:
        model = models.Group
        fields = {
            'id': ['exact'],
            'subject': ['exact'],
            'days_type': ['exact'],
            'start_time': ['exact'],
            'current_teacher': ['exact'],
        }

    def by_student(self, queryset, field_name, value, *args, **kwargs):
        if value == 'not_enough':
            return queryset.filter(student_count__lt=F('max_student_count'))
        if value == 'over':
            return queryset.filter(student_count__gt=F('max_student_count'))
        return queryset.filter(student_count=F('max_student_count'))
