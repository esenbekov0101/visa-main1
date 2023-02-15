from django_filters.rest_framework import FilterSet

from .. import models


class AttendanceFilter(FilterSet):
    class Meta:
        model = models.Lesson
        fields = {
            'completion_timestamp': ['gte', 'lte', 'range'],
            'took_place': ['exact'],
            'studentlesson__student': ['exact'],
            'group': ['exact'],
        }
